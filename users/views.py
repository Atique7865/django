from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import DeleteView, DetailView, FormView, ListView, TemplateView

from . import services
from .forms import ManagedUserCreateForm, ManagedUserUpdateForm


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self) -> bool:
        return self.request.user.is_staff

    def handle_no_permission(self) -> HttpResponse:
        if self.request.user.is_authenticated:
            raise PermissionDenied("You must be a staff member to access this page.")
        return super().handle_no_permission()


class UserLoginView(LoginView):
    template_name = "registration/login.html"
    redirect_authenticated_user = True


def home(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect("dashboard")
    return redirect("login")


class DashboardView(StaffRequiredMixin, TemplateView):
    template_name = "users/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(services.get_dashboard_metrics())
        return context


class UserListView(StaffRequiredMixin, ListView):
    template_name = "users/user_list.html"
    context_object_name = "managed_users"
    paginate_by = 10

    def get_queryset(self):
        self.query = self.request.GET.get("q", "").strip()
        return services.list_managed_users(self.query)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = getattr(self, "query", "")
        return context


class UserDetailView(StaffRequiredMixin, DetailView):
    template_name = "users/user_detail.html"
    context_object_name = "managed_user"

    def get_object(self, queryset=None):
        return services.get_managed_user(self.kwargs["pk"])


class UserCreateView(StaffRequiredMixin, FormView):
    template_name = "users/user_form.html"
    form_class = ManagedUserCreateForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_title"] = "Create user"
        context["submit_label"] = "Create user"
        return context

    def form_valid(self, form):
        managed_user = services.create_managed_user(form.cleaned_data)
        messages.success(self.request, f"User '{managed_user.username}' was created.")
        return redirect("user-detail", pk=managed_user.pk)


class UserUpdateView(StaffRequiredMixin, FormView):
    template_name = "users/user_form.html"
    form_class = ManagedUserUpdateForm

    def dispatch(self, request, *args, **kwargs):
        self.managed_user = services.get_managed_user(kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["instance"] = self.managed_user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_title"] = f"Edit {self.managed_user.username}"
        context["submit_label"] = "Save changes"
        context["managed_user"] = self.managed_user
        return context

    def form_valid(self, form):
        managed_user = services.update_managed_user(self.managed_user, form.cleaned_data)
        if managed_user.pk == self.request.user.pk and form.cleaned_data.get("password1"):
            update_session_auth_hash(self.request, managed_user)
        messages.success(self.request, f"User '{managed_user.username}' was updated.")
        return redirect("user-detail", pk=managed_user.pk)


class UserDeleteView(StaffRequiredMixin, DeleteView):
    template_name = "users/user_confirm_delete.html"
    success_url = reverse_lazy("user-list")
    context_object_name = "managed_user"

    def get_object(self, queryset=None):
        return services.get_managed_user(self.kwargs["pk"])

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object == request.user:
            messages.error(request, "You cannot delete the account you are currently signed in with.")
            return redirect("user-detail", pk=self.object.pk)

        username = self.object.username
        services.delete_managed_user(self.object)
        messages.success(request, f"User '{username}' was deleted.")
        return redirect(self.success_url)

