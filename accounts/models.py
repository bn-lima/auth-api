from django.db import models
from django.contrib.auth.models import AbstractUser

class Account(AbstractUser):
    profile = models.ImageField(default="accounts/default.png", blank=True, null=True)
    email = models.EmailField(max_length=250, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return f'{self.email} - {self.username}'