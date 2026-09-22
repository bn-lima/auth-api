from django.contrib import admin
from .models import Account, ResetPasswordToken, PendingAccountRegistration, PendingRegistrationToken

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "profile", "cpf", "phone")
    search_fields = ("username", "email", "cpf", "phone")

@admin.register(ResetPasswordToken)
class ResetPasswordTokenAdmin(admin.ModelAdmin):
    list_display = ("account__email", "created_at", "key", "expires_at", "expired", "active")
    search_fields = ("account__email", "created_at", "key", "expires_at")
    list_filter = ("expired", "active")

@admin.register(PendingAccountRegistration)
class RequestAccountRegistrationSerializerAdmin(admin.ModelAdmin):
    list_display = ("email", "created_at", "expires_at")
    search_fields = ("email", "created_at", "expires_at")

@admin.register(PendingRegistrationToken)
class PendingRegistrationTokenAdmin(admin.ModelAdmin):
    list_display = ("pending_registration__email", "key", "created_at", "expires_at", "expired", "active")
    search_fields = ("pending_registration__email", "key", "created_at", "expires_at")
    list_filter = ("expired", "active")
