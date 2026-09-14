from .models import Account
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from django.utils import timezone

def authenticate_account(email, password): # Verifica se existe um usuário com as credenciais passadas
    account = authenticate(email=email, password=password) # Verifica se o usuário existe no banco

    if not account:
        return None
    return account

def generate_account_tokens(account): # Gera tokens de autenticação para o usuário
    refresh = RefreshToken.for_user(account) # Gera refresh_token para o usuário

    return str(refresh.access_token), str(refresh) # Retorna refresh e access token

def revoke_account_refresh_tokens(account): # Desativa todos os refresh tokens do usuário
    tokens = OutstandingToken.objects.filter(user=account)

    for token in tokens:
        BlacklistedToken.objects.get_or_create(token=token)

def expire_account_reset_password_tokens(account): # Inativa tokens de reset expirados de um conta

    account.reset_password_tokens.filter( # Filtra tokens ativos com a data expirada
        active=True,
        expired=False,
        expires_at__lte=timezone.now()
    ).update(
        active=False,
        expired=True
    )

def get_account_by_email(email): # Pega account pelo email
    try:
        account = Account.objects.get(email=email)
    except Account.DoesNotExist:
        return None
    return account