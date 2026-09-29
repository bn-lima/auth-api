from django.urls import path, include
from .views import LoginAccountView, RefreshTokenView, LogoutAccountView, ResetPasswordRequestView, ForgotPasswordView, ResetPasswordView, IsAuthenticated, RequestAccountRegistrationView, ConfirmAccountRegistrationView, AddPhoneNumberView, ConfirmPhoneNumberView

urlpatterns = [
    path("register/", include([
        path("request/", RequestAccountRegistrationView.as_view(), name="request_account_registration"), # Solicita registro de conta por email
        path("confirm/<str:registration_token>/", ConfirmAccountRegistrationView.as_view(), name="cofirm_account_registration"), # Confirma registro de conta
    ])),

    path("login/", LoginAccountView.as_view(), name="login_account"), # Loga um usuário
    path("refresh/", RefreshTokenView.as_view(), name="refresh_account_token"), # Gera um novo token de acesso usando um refresh_token
    path("logout/", LogoutAccountView.as_view(), name="logout_account"), # Realiza logout
    path("authenticated/", IsAuthenticated.as_view(), name="is_account_authenticated"), # Testa se o usuário está autenticado

    path("password/", include([
        path("reset/", include([
            path("request/", ResetPasswordRequestView.as_view(), name="request_password_reset"),# Requisita uma troca de senha
            path("forgot/", ForgotPasswordView.as_view(), name="forgot_password_request"), # Requisita troca de senha para usuários não logados
            path("<str:reset_token>", ResetPasswordView.as_view(), name="reset_account_password") # Troca a senha da conta
        ]))
    ])),

    path("phone/", include([
        path("send-code/", AddPhoneNumberView.as_view(), name="send_sms_code"),
        path("confirm/", ConfirmPhoneNumberView.as_view(), name="confirm_account_phone")
    ]))
]