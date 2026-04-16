from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class UserManagementViewsTests(TestCase):
    def setUp(self):
        self.staff_user = User.objects.create_user(
            username="adminuser",
            password="AdminPass123!",
            email="admin@example.com",
            is_staff=True,
        )

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_staff_user_can_create_managed_user(self):
        self.client.force_login(self.staff_user)
        response = self.client.post(
            reverse("user-create"),
            {
                "username": "janedoe",
                "first_name": "Jane",
                "last_name": "Doe",
                "email": "jane@example.com",
                "is_staff": "on",
                "is_active": "on",
                "password1": "UserPass123!",
                "password2": "UserPass123!",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username="janedoe").exists())

    def test_non_staff_user_gets_forbidden(self):
        regular_user = User.objects.create_user(
            username="basicuser",
            password="BasicPass123!",
        )
        self.client.force_login(regular_user)
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 403)
