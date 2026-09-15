from django.urls import path, include
from .views import RegisterAccountView, LoginAccountView, RefreshTokenView, LogoutAccountView, ResetPasswordRequestView, ForgotPasswordView, ResetPasswordView

urlpatterns = [
    path("register/", RegisterAccountView.as_view(), name="register_account"), # Registra uma conta
    path("login/", LoginAccountView.as_view(), name="login_account"), # Loga um usuário
    path("refresh/", RefreshTokenView.as_view(), name="refresh_account_token"), # Gera um novo token de acesso usando um refresh_token
    path("logout/", LogoutAccountView.as_view(), name="logout_account"), # Realiza logout

    path("password/", include([
        path("reset/", include([
            path("request/", ResetPasswordRequestView.as_view(), name="request_password_reset"),# Requisita uma troca de senha
            path("forgot/", ForgotPasswordView.as_view(), name="forgot_password_request"), # Requisita troca de senha para usuários não logados
            path("<str:reset_token>", ResetPasswordView.as_view(), name="reset_account_password") # Troca a senha da conta
        ]))
    ]))
]