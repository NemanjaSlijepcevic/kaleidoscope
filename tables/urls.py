from django.urls import path
from .views import (
    AuthorAutocomplete,
    CategoryAutocomplete,
    PlaceAutocomplete,
    YearAutocomplete,
    ImageCreateView,
    ImageDeleteView,
    ImageListView,
    ImageUpdateView,
    ImageWatermarkedView,
)


app_name = 'images'
urlpatterns = [
    path(
        '',
        ImageListView.as_view(),
        name='image-list'
    ),
    path(
        'create/',
        ImageCreateView.as_view(),
        name='image-create'
    ),
    path(
        '<int:pk>/delete/',
        ImageDeleteView.as_view(),
        name='image-delete'
    ),
    path(
        '<int:pk>/update/',
        ImageUpdateView.as_view(),
        name='image-update'
    ),
    path(
        '<int:pk>/watermarked/',
        ImageWatermarkedView.as_view(),
        name='image-watermarked'
    ),
    path(
        'author-autocomplete/',
        AuthorAutocomplete.as_view(create_field='name', validate_create=True),
        name='author-autocomplete'
    ),
    path(
        'category-autocomplete/',
        CategoryAutocomplete.as_view(create_field='name', validate_create=True),
        name='category-autocomplete'
    ),
    path(
        'place-autocomplete/',
        PlaceAutocomplete.as_view(create_field='name', validate_create=True),
        name='place-autocomplete'
    ),
    path(
        'year-autocomplete/',
        YearAutocomplete.as_view(create_field='name', validate_create=True),
        name='year-autocomplete'
    ),
]
