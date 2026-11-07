from django.urls import path

from . import views

urlpatterns = [
    path(r"me", views.UserProfileView.as_view(), name="me"),
    path(r"login", views.LoginView.as_view(), name="login"),
]
