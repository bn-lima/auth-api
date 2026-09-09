from .models import Account
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

def authenticate_account(email, password): # Verifica se existe um usuário com as credenciais passadas
    account = authenticate(email=email, password=password) # Verifica se o usuário existe no banco

    if not account:
        return None
    return account

def generate_account_tokens(account): # Gera tokens de autenticação para o usuário
    refresh = RefreshToken.for_user(account) # Gera refresh_token para o usuário

    return str(refresh.access_token), str(refresh) # Retorna refresh e access token