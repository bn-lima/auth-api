from rest_framework import serializers
from .models import Account, PendingAccountRegistration, PendingRegistrationToken
from .validators import PASSWORD_VALIDATOR, EMAIL_VALIDATOR
from .services import authenticate_account, generate_account_tokens, expire_account_reset_password_tokens, get_account_by_email, validate_reset_password_token, deactivate_all_account_reset_password_tokens
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from .models import ResetPasswordToken
from .email import send_password_reset_email, send_registration_request_email

class RequestAccountRegistrationSerializer(serializers.Serializer): # ializer responsável por solicitar registro de conta
    email = serializers.CharField(
        max_length=250,
        validators=[EMAIL_VALIDATOR],
        required=True
    )

    def validate(self, data):

        if Account.objects.filter(email=data.get("email")).exists(): # Verifica se já existe uma conta com esse email
            raise serializers.ValidationError("An account with this email already exists")

        pending_registration, created = PendingAccountRegistration.objects.get_or_create( # Pega ou cria pending_registration com o email passado
            email=data.get("email")
        )

        if not created: # Verifica se o registro foi criado agora

            if pending_registration.delete_if_expired(): # Deleta o registro se estiver expirado
                raise serializers.ValidationError("The registration request has expired. Please request a new registration")
            
            pending_registration.expire_registration_tokens() # Desativa tokens de registro expirados

            if pending_registration.count_active_registration_tokens() >= 3: # Verifica se o registro possui 3 ou mais tokens ativos
                raise serializers.ValidationError("Maximum of 3 active registration tokens reached for this email address")

        data["pending_registration"] = pending_registration
        return data

    def save(self, **kwargs):
        pending_registration = self.validated_data.get("pending_registration") # Pega pending_registration dos dados validados

        registration_token = PendingRegistrationToken.objects.create( # Cria token de registro associado a pending_registration
            pending_registration=pending_registration,
        )

        send_registration_request_email( # Envia link de registro por email
            pending_registration.email,
            registration_token.key
        )

        return registration_token

class LoginAccountSerializer(serializers.Serializer): # Serializer responsável por logar o usuário
    email = serializers.EmailField(max_length=250, required=True)
    password = serializers.CharField(max_length=128, required=True, write_only=True)

    def validate(self, data):

        account = authenticate_account(data.get("email"), data.get("password"))

        if not account:
            raise serializers.ValidationError("invalid credentials")

        data["account"] = account
        return data

    def save(self, **kwargs):
        account = self.validated_data.get("account")

        access_token, refresh_token = generate_account_tokens(account) # Cria access_token e refresh_token relacionado a conta

        return access_token, refresh_token

class RefreshTokenSerializer(serializers.Serializer): # Gera novo token de acesso
    refresh_token = serializers.CharField(
        max_length=600,
        required=True,
        write_only=True
    )

    def validate(self, data):

        try:
            refresh = RefreshToken(data.get("refresh_token")) # Verifica se refresh_token é válido
        except TokenError:
            raise serializers.ValidationError("invalid refresh_token")

        data["refresh"] = refresh
        return data

    def save(self, **kwargs):
        refresh = self.validated_data.get("refresh")

        return str(refresh.access_token) # Devolve novo token de acesso

class ResetPasswordRequestSerializer(serializers.Serializer): # Cria reset password e envia por email

    def validate(self, data):
        account = self.context.get("account")

        expire_account_reset_password_tokens(account)

        if account.has_too_many_reset_tokens(): # Verifica se a conta possui 3 ou mais tokens de reset de senha
            raise serializers.ValidationError("You have reached the limit of 3 active password reset requests")

        data["account"] = account # Adiciona account nos dados validados
        return data

    def create(self, validated_data):
        account = validated_data.get("account")

        reset_token = ResetPasswordToken.objects.create(account=account) # Cria objeto reset token
        send_password_reset_email(account.email, reset_token.key) # Envia email de recuperação

        return reset_token

class ForgotPasswordSerializer(serializers.Serializer): # Cria reset password e envia por email (para usuários não logados) 
    email = serializers.EmailField(max_length=250, required=True)

    def validate(self, data):
        account = get_account_by_email(data.get("email")) # Verifica se uma conta com esse email existe

        if not account: # Retorna erro caso não exista
            raise serializers.ValidationError("An account with this email does not exist")

        expire_account_reset_password_tokens(account) # Inativa os tokens de reset de senha expirados

        if account.has_too_many_reset_tokens(): # Verifica se a conta possui 3 ou mais tokens de reset de senha
            raise serializers.ValidationError("You have reached the limit of 3 active password reset requests")

        data["account"] = account
        return data

    def create(self, validated_data):
        account = validated_data.get("account")

        reset_token = ResetPasswordToken.objects.create(account=account) # Cria token de reset de senha

        send_password_reset_email(account.email, reset_token.key) # Envia o token para o email do usuário

        return reset_token

class ResetPasswordSerializer(serializers.Serializer): # Serializer responsável por trocar a senha da conta
    new_password = serializers.CharField(max_length=128, validators=[PASSWORD_VALIDATOR], write_only=True)
    confirm_new_password = serializers.CharField(max_length=128, validators=[PASSWORD_VALIDATOR], write_only=True)

    def validate(self, data):
        str_reset_token = self.context.get("reset_token") # Pega a string do token de reset passado na view

        reset_token = validate_reset_password_token(str_reset_token) # Valida o token de reset

        if not reset_token: # Verifica se o token é válido
            raise serializers.ValidationError("invalid reset_token")

        new_password = data.get("new_password") # Pega a nova senha

        if new_password != data.get("confirm_new_password"): # Verifica se as senhas são iguais
            raise serializers.ValidationError("passwords do not match")

        account = reset_token.account # Pega a conta relacionada ao token de reset

        if account.check_password(new_password): # Verifica se a senha atual é igual a nova senha
            raise serializers.ValidationError("the new password cannot be the same as your current password")

        data["account"] = account 
        return data

    def save(self, **kwargs):
        account = self.validated_data.get("account") # Pega a conta dos dados validados

        account.set_password(self.validated_data.get("new_password")) # Define nova senha
        account.save(update_fields=["password"])
        # Desativa todos os reset password tokens da conta
        deactivate_all_account_reset_password_tokens(account)

        return account