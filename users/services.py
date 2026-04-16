from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Q, QuerySet
from django.shortcuts import get_object_or_404


def get_dashboard_metrics() -> dict:
    recent_users = User.objects.order_by("-date_joined")[:5]
    return {
        "total_users": User.objects.count(),
        "active_users": User.objects.filter(is_active=True).count(),
        "staff_users": User.objects.filter(is_staff=True).count(),
        "recent_users": recent_users,
    }


def list_managed_users(query: str = "") -> QuerySet[User]:
    users = User.objects.all().order_by("username")
    if query:
        users = users.filter(
            Q(username__icontains=query)
            | Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
            | Q(email__icontains=query)
        )
    return users


def get_managed_user(user_id: int) -> User:
    return get_object_or_404(User, pk=user_id)


@transaction.atomic
def create_managed_user(cleaned_data: dict) -> User:
    payload = cleaned_data.copy()
    password = payload.pop("password1")
    payload.pop("password2", None)
    return User.objects.create_user(password=password, **payload)


@transaction.atomic
def update_managed_user(user: User, cleaned_data: dict) -> User:
    payload = cleaned_data.copy()
    password = payload.pop("password1", "")
    payload.pop("password2", None)

    for field, value in payload.items():
        setattr(user, field, value)

    if password:
        user.set_password(password)

    user.save()
    return user


@transaction.atomic
def delete_managed_user(user: User) -> None:
    user.delete()
