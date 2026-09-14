from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
from django.utils import timezone
from datetime import timedelta

class Account(AbstractUser):
    profile = models.ImageField(default="accounts/default.png", blank=True, null=True)
    email = models.EmailField(max_length=250, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return f'{self.email} - {self.username}'

def get_expiration_time():
    return timezone.now() + timedelta(minutes=15)

class ResetPasswordToken(models.Model): # Token de redefinição de senha
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="reset_password_tokens")
    created_at = models.DateTimeField(auto_now_add=True)
    key = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    active = models.BooleanField(default=True)
    expired = models.BooleanField(default=False)
    expires_at = models.DateTimeField(default=get_expiration_time)

    def mark_as_expired(self): # Marca token como expirado e inativo
        self.active = False
        self.expired = True
        self.save(update_fields=["active", "expired"])

    def is_expired(self): # Verifica se o token expirou
        return self.expires_at < timezone.now()

    def __str__(self):
        return f"{self.account.email} - {self.key}"