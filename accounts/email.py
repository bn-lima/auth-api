from django.core.mail import EmailMessage

def send_test_email(email, reset_token): # Envia email de reset de senha
    # MUDAR A URL PARA PRODUÇÃO
    url = f"http://localhost:8000/account/password/reset/{reset_token}"

    email_message = EmailMessage(
        subject="Password Reset Request",
        body=f"Hello, we received a request to reset your password.\nUse the link below to reset your password:\n{url}\nIf you did not request a password reset, you can safely ignore this email.",
        to=[email]
    )

    email_message.send(fail_silently=False)