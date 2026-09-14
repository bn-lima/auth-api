from django.contrib import admin
from .models import Account, ResetPasswordToken

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "profile")
    search_fields = ("username", "email")

@admin.register(ResetPasswordToken)
class ResetPasswordTokenAdmin(admin.ModelAdmin):
    list_display = ("account__email", "created_at", "key", "expires_at", "expired", "active")
    search_fields = ("account__email", "created_at", "key", "expires_at")
    list_filter = ("expired", "active")