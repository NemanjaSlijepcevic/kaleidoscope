from django.urls import reverse, reverse_lazy
from django.db.models import F, Min, Q, Prefetch
from django.http import Http404, JsonResponse, HttpRequest, HttpResponse
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.core.paginator import Paginator
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.utils.translation import gettext_lazy as _
from django.views.generic import (
    CreateView,
    DeleteView,
    ListView,
    UpdateView,
    View
)
from .forms import ImageForm
from .models import (
    Author,
    Image,
    Category,
    Place,
    Year
)
from .search import fold
from dal import autocomplete
from .utils import user_in_group


class ModelAutocomplete(autocomplete.Select2QuerySetView):
    model = None
    name_field = 'name'

    def get_queryset(self):
        if self.model is None:
            raise ValueError("The 'model' attribute must be set on ModelAutocomplete subclasses.")

        if not self.request.user.is_authenticated:
            return self.model.objects.none()

        qs = self.model.objects.all()

        if self.q:
            # Same normalisation as the gallery search, so typing an author in
            # Latin or in lower-case Cyrillic finds them. Year has no
            # normalised copy - it stores an integer - so it keeps the plain
            # lookup, which is fine for digits.
            if hasattr(self.model, "search_key"):
                qs = qs.filter(search_key__startswith=fold(self.q))
            else:
                qs = qs.filter(name__istartswith=self.q)
        return qs


class AuthorAutocomplete(ModelAutocomplete):
    model = Author


class CategoryAutocomplete(ModelAutocomplete):
    model = Category


class PlaceAutocomplete(ModelAutocomplete):
    model = Place


class YearAutocomplete(ModelAutocomplete):
    model = Year


class UserPassesGroupTest(UserPassesTestMixin):
    request_group = ''

    def test_func(self):
        return user_in_group(self.request.user, self.request_group)

    def handle_no_permission(self):
        raise PermissionDenied


class ImageCreateView(LoginRequiredMixin, UserPassesGroupTest, CreateView):
    model = Image
    form_class = ImageForm
    success_url = reverse_lazy("images:image-create")
    request_group = "Add"

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_create"] = True
        return context


class ImageDeleteView(LoginRequiredMixin, UserPassesGroupTest, DeleteView):
    model = Image
    request_group = "Delete"
    success_url = reverse_lazy("images:image-list")

    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if request.method == "POST" and request.headers.get("X-Requested-With") == "XMLHttpRequest":
            try:
                obj = self.get_object()
                obj.delete()
                return JsonResponse({"message": _("Image deleted successfully")}, status=200)
            except ObjectDoesNotExist:
                return JsonResponse({"error": _("Image not found")}, status=404)
            except Exception as e:
                return JsonResponse({"error": str(e)}, status=500)
        return super().dispatch(request, *args, **kwargs)


class ImageWatermarkedView(View):
    def get(self, request, pk):
        image = get_object_or_404(Image, pk=pk)
        if not image.image:
            raise Http404("Image has no source file")
        return redirect(image.watermarked.url)


class ImageListView(ListView):
    model = Image
    # Matches the default option in partials/pagination.html.
    paginate_by = 24

    def get_queryset(self):
        queryset = Image.objects.all()
        search_text = self.request.GET.get("search-field", "").strip()
        author_filter = self.request.GET.get("author")
        place_filter = self.request.GET.get("place")
        year_filter = self.request.GET.get("year")
        category_filters = self.request.GET.getlist("category")

        if search_text:
            # Match on the normalised copies rather than the stored text, so a
            # Cyrillic query is case-insensitive, a Latin query finds Cyrillic
            # records, and њ matches н + ј. tables/search.py explains it.
            key = fold(search_text)
            if key:
                queryset = queryset.filter(
                    Q(search_key__contains=key) |
                    Q(author__search_key__contains=key) |
                    Q(category__search_key__contains=key) |
                    Q(place__search_key__contains=key) |
                    # Years are digits, which need no folding.
                    Q(year__name__icontains=search_text)
                ).distinct()

        if author_filter:
            queryset = queryset.filter(author__id=author_filter)

        if place_filter:
            queryset = queryset.filter(place__id=place_filter)

        if year_filter:
            queryset = queryset.filter(year__id=year_filter)

        if category_filters:
            for category_id in category_filters:
                queryset = queryset.filter(category__id=category_id)

        if (author_filter or place_filter or year_filter or category_filters) and search_text:
            queryset = queryset.distinct()

        sort_column = self.request.GET.get("sort", "id")
        order = self.request.GET.get("order", "asc")
        queryset = queryset.annotate(
            author_sort=Min('author__sort_key'),
            category_sort=Min('category__sort_key'),
        )
        sort_mapping = {
            "id": "id",
            "author": "author_sort",
            "title": "sort_key",
            "place": "place__sort_key",
            "year": "year__name",
            "category": "category_sort"
        }

        if sort_column in sort_mapping:
            sort_field = F(sort_mapping[sort_column])
            # An image with no author or no year must not lead the list on the
            # strength of a NULL, which is where SQLite puts it by default.
            if order == "desc":
                queryset = queryset.order_by(sort_field.desc(nulls_last=True))
            else:
                queryset = queryset.order_by(sort_field.asc(nulls_last=True))

        queryset = queryset.prefetch_related(
            Prefetch('author', queryset=Author.objects.only('name')),
            Prefetch('category', queryset=Category.objects.only('name')),
        ).select_related('place', 'year')
        return queryset

    def get(self, request, *args, **kwargs):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            images = self.get_queryset()
            paginate_by = request.GET.get("paginate_by", str(self.paginate_by))
            login = request.user.is_authenticated

            if paginate_by == "all":
                page_obj = images
                total_pages = 1
            else:
                paginate_by = int(paginate_by)
                paginator = Paginator(images, paginate_by)
                page_number = request.GET.get("page", 1)
                page_obj = paginator.get_page(page_number)
                total_pages = paginator.num_pages

            data = [
                {
                    "id": image.pk,
                    "title": image.title,
                    "image_url": (
                        reverse("images:image-watermarked", args=[image.pk])
                        if image.image else ""
                    ),
                    "thumbnail_url": image.thumbnail.url if image.image else "",
                    "description": image.description,
                    "authors": [author.name for author in image.author.all()],
                    "place": image.place.name if image.place else "",
                    "year": image.year.name if image.year else "",
                    "categories": [category.name for category in image.category.all()],
                    "detail_url": image.get_absolute_url() if login else "",
                }
                for image in page_obj
            ]

            return JsonResponse({
                "images": data,
                "can_edit": self.request.user.is_superuser or self.request.user.groups.filter(name="Edit").exists(),  # noqa: E501
                "has_next": getattr(page_obj, "has_next", lambda: False)(),
                "current_page": getattr(page_obj, "number", 1),
                "total_pages": total_pages
            }, safe=False)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) | {
            "authors": Author.objects.all(),
            "places": Place.objects.all(),
            "years": Year.objects.all(),
            "categories": Category.objects.all(),
            "selected_author": self.request.GET.get("author", ""),
            "selected_place": self.request.GET.get("place", ""),
            "selected_year": self.request.GET.get("year", ""),
            "selected_categories": self.request.GET.getlist("category"),
        }
        return context


class ImageUpdateView(LoginRequiredMixin, UserPassesGroupTest, UpdateView):
    model = Image
    form_class = ImageForm
    request_group = "Edit"
    success_url = reverse_lazy("images:image-list")

    def form_valid(self, form):
        form.instance.edited_by = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs) | {
            "is_create": False,
            "object": self.get_object(),
        }
