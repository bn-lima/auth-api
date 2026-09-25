from .models import Account, ResetPasswordToken, PendingRegistrationToken
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from django.utils import timezone
import uuid

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

def validate_reset_password_token(str_reset_token): # Valida reset password token

    try:
        uuid_reset_token = uuid.UUID(str_reset_token) # Verifica se o formato é válido
    except ValueError:
        return None

    try:
        reset_token = ResetPasswordToken.objects.get(key=uuid_reset_token) # Verifica se existe um token com esse uuid no banco
    except ResetPasswordToken.DoesNotExist:
        return None

    if reset_token.expires_at <= timezone.now(): # Verifica se o token expirou e marca como inativo
        reset_token.expired = True
        reset_token.active = False
        reset_token.save(update_fields=["expired", "active"])
        return None

    if not reset_token.active: # Verifica se o token está ativo
        return None
    
    return reset_token

def deactivate_all_account_reset_password_tokens(account): # Desativa todos os tokens da conta

    account.reset_password_tokens.filter(
        active=True,
        expired=False
    ).update(active=False)

def validate_registration_token(str_registration_token): # Valida objeto PendingRegistrationToken
    # Tenta converter a string recebida para um UUID válido
    try: 
        uuid_registration_token = uuid.UUID(str_registration_token)
    except ValueError:
        return None
    # Busca o token no banco de dados usando o UUID
    try: 
        registration_token = PendingRegistrationToken.objects.get(key=uuid_registration_token)
    except PendingRegistrationToken.DoesNotExist:
        return None
    # Verifica se o token já está expirado ou desativado
    if registration_token.expired or  not registration_token.active:
        return None
    # Verifica se a data de expiração já passou
    if registration_token.expires_at < timezone.now():
        registration_token.expired = True
        registration_token.active = False
         # Salva somente os campos que foram alterados
        registration_token.save(update_fields=["expired", "active"])
        return None
    # Retorna o token se ele ainda for válido
    return registration_token

def complete_registration(registration_token): # Finaliza a confirmação de registro
    # Deleta registro pendente
    registration_token.pending_registration.delete()