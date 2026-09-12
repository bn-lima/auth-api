from django.urls import path
from .views import RegisterAccountView, LoginAccountView, RefreshTokenView, LogoutAccountView

urlpatterns = [
    path("register/", RegisterAccountView.as_view(), name="register_account"), # Registra uma conta
    path("login/", LoginAccountView.as_view(), name="login_account"), # Loga um usuário
    path("refresh/", RefreshTokenView.as_view(), name="refresh_account_token"), # Gera um novo token de acesso usando um refresh_token
    path("logout/", LogoutAccountView.as_view(), name="logout_account") # Realiza logout
]