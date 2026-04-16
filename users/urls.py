from django.contrib.auth.views import LogoutView
from django.urls import path

from .views import (
    DashboardView,
    UserCreateView,
    UserDeleteView,
    UserDetailView,
    UserListView,
    UserLoginView,
    UserUpdateView,
    home,
)

urlpatterns = [
    path("", home, name="home"),
    path("login/", UserLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("users/", UserListView.as_view(), name="user-list"),
    path("users/create/", UserCreateView.as_view(), name="user-create"),
    path("users/<int:pk>/", UserDetailView.as_view(), name="user-detail"),
    path("users/<int:pk>/edit/", UserUpdateView.as_view(), name="user-update"),
    path("users/<int:pk>/delete/", UserDeleteView.as_view(), name="user-delete"),
]

