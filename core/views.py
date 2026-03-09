from django.core.exceptions import PermissionDenied
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView, PasswordChangeView
from .forms import SignupForm, UserEditForm
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.generic import (
    CreateView,
    DeleteView,
    ListView,
    UpdateView
)


class SuperUserRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        raise PermissionDenied


class UserRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        obj = self.get_object()
        return self.request.user.is_superuser or self.request.user.pk == obj.pk

    def handle_no_permission(self):
        raise PermissionDenied


class UserCreateView(LoginRequiredMixin, SuperUserRequiredMixin, CreateView):
    model = User
    form_class = SignupForm
    success_url = reverse_lazy("users:user-create")
    permission_required = 'auth.change_user'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['is_superuser'] = self.request.user.is_superuser
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_superuser'] = self.request.user.is_superuser
        context['is_create'] = True
        return context


class UserDeleteView(LoginRequiredMixin, SuperUserRequiredMixin, DeleteView):
    model = User
    success_url = reverse_lazy("users:user-list")

    def dispatch(self, request, *args, **kwargs):
        if request.method == "POST" and request.headers.get("X-Requested-With") == "XMLHttpRequest":
            self.object = self.get_object()
            self.object.delete()
            return JsonResponse({"message": "User deleted successfully"}, status=200)
        return super().dispatch(request, *args, **kwargs)


class UserListView(LoginRequiredMixin, SuperUserRequiredMixin, ListView):
    model = User


class UserLoginView(LoginView):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(self.get_success_url())
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy("images:image-list")


class UserPasswordView(PasswordChangeView, UserRequiredMixin):
    template_name = 'registration/password.html'
    success_url = reverse_lazy('users:user-update')


class UserUpdateView(LoginRequiredMixin, UserRequiredMixin, UpdateView):
    model = User
    form_class = UserEditForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['is_superuser'] = self.request.user.is_superuser
        return kwargs

    def form_valid(self, form):
        form.instance.edited_by = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_create'] = False
        context['object'] = self.get_object()
        return context

    def get_success_url(self):
        if self.request.user.is_superuser:
            return reverse_lazy("users:user-list")
        return reverse_lazy("users:user-update", kwargs={"pk": self.request.user.pk})
