from django.urls import path
from .views import login_view, register_user, forgot_password_view, force_change_password_view
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('login/', login_view, name="login"),
    path('register/', register_user, name="register"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path('forgot-password/', forgot_password_view, name="forgot_password"),
    path('force-change-password/', force_change_password_view, name="force_change_password"),
]
