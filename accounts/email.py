from django.core.mail import EmailMessage

def send_password_reset_email(email, reset_token): # Envia email de reset de senha
    # MUDAR A URL PARA PRODUÇÃO
    url = f"http://localhost:8000/account/password/reset/{reset_token}"

    email_message = EmailMessage(
        subject="Password Reset Request",
        body=f"Hello, we received a request to reset your password.\nUse the link below to reset your password:\n{url}\nIf you did not request a password reset, you can safely ignore this email.",
        to=[email]
    )

    email_message.send(fail_silently=False)

def send_registration_request_email(email, registration_token): # Envia email para registrar a conta
    # MUDAR A URL PARA PRODUÇÃO
    url = f"http://localhost:8000/account/register/confirm/{registration_token}/"
    
    email_message = EmailMessage(
        subject="Account Registration Request",
        body=f"Hello, we received a request to create an account using this email address.\nUse the link below to complete your registration:\n{url}\nThis link will expire in 15 minutes.\nIf you did not request an account registration, you can safely ignore this email.",
        to=[email]
    )

    email_message.send()

def send_account_deletion_email(username, email, deletion_token): # Envia token de exclusão de conta por email
    # MUDAR A URL PARA PRODUÇÃO
    url = f"http://localhost:8000/account/delete/{deletion_token}/"

    email_message = EmailMessage(
        subject="Confirm your account deletion",
        body = (
            f"Hi {username},\n\n"
            "We received a request to delete your account.\n\n"
            "To confirm, open the link below:\n"
            f"{url}\n\n"
            "If you didn't request this, ignore this email and your account will "
            "remain active. We also recommend changing your password.\n"
        ),
        to=[email]
    )

    email_message.send()