from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    UserCreateView,
    UserDeleteView,
    UserListView,
    UserLoginView,
    UserPasswordView,
    UserUpdateView,
)


app_name = 'users'
urlpatterns = [
    path('', UserListView.as_view(), name='user-list'),
    path('signup/', UserCreateView.as_view(), name='user-create'),
    path('<int:pk>/delete/', UserDeleteView.as_view(), name='user-delete'),
    path('<int:pk>/password/', UserPasswordView.as_view(), name='user-password'),
    path('<int:pk>/update/', UserUpdateView.as_view(), name='user-update'),
    path('login/', UserLoginView.as_view(next_page='images:image-list'), name='user-login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='users:user-login'), name='user-logout'),

]
