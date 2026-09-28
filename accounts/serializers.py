from rest_framework import serializers
from .models import Account, PendingAccountRegistration, PendingRegistrationToken
from .validators import PASSWORD_VALIDATOR, EMAIL_VALIDATOR, PHONE_VALIDATOR
from .services import authenticate_account, generate_account_tokens, expire_account_reset_password_tokens, get_account_by_email, validate_reset_password_token, deactivate_all_account_reset_password_tokens, validate_registration_token, complete_registration, invalidate_expired_sms_codes, is_phone_used
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from .models import ResetPasswordToken, SMSCode
from .email import send_password_reset_email, send_registration_request_email
from django.db import transaction
from .sms import send_sms_code

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

class ConfirmAccountRegistrationSerializer(serializers.ModelSerializer): # Confirma o registro de uma conta
    confirm_password = serializers.CharField( # Campo para confirmação de senha 
        max_length=250,
        required=True,
        write_only=True,
        validators=[PASSWORD_VALIDATOR]
    )
    class Meta:
        model = Account
        exclude = ("created_at", "email")

        extra_kwargs = { # Adiciona validador de senha no campo password
            "password": {
                "validators":[PASSWORD_VALIDATOR]
            }
        }

    def validate(self, data):
        # Pega registration_token do context
        str_registration_token = self.context.get("registration_token")

        # Verifica se o token passado é válido
        registration_token = validate_registration_token(str_registration_token)

        # Retorna erro caso seja inválido
        if not registration_token:
            raise serializers.ValidationError("invalid registration_token")
        
        # Verifica se password e confirm_password são iguais
        if data.get("password") != data.get("confirm_password"):
            raise serializers.ValidationError("passwords do not match")

        # Verifica se existe um usuário com o mesmo username
        if Account.objects.filter(username=data.get("username")).exists():
            raise serializers.ValidationError("an account with this username already exists")
        
        # Adiciona registration_token nos dados validados
        data["registration_token"] = registration_token
        return data

    @transaction.atomic()
    def create(self, validated_data):
        registration_token_id = validated_data.pop("registration_token") # Remove registration_token dos dados validados e armazena na variável registration_token_id
        password = validated_data.pop("password") # Remove password dos dados validados e adiciona na variável password
        validated_data.pop("confirm_password") # Remove confirm_password dos dados validados

        # Busca o token de registro e seu pending_registration relacionado  
        registration_token = PendingRegistrationToken.objects.select_for_update(
        ).select_related("pending_registration").get(id=registration_token_id.id)

        account = Account.objects.create( # Cria conta sem senha
            **validated_data,
            email=registration_token.pending_registration.email
        )

        account.set_password(password) # Define senha criptografada
        account.save(update_fields=["password"]) # Salva a conta com a senha definida

        complete_registration(registration_token) # Finaliza a confirmação de registro

        return account

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

class AddPhoneNumberSerializer(serializers.Serializer): # Envia código de sms
    phone = serializers.CharField(
        required=True,
        validators=[PHONE_VALIDATOR]
    )

    def validate(self, data):
        authenticated_account = self.context.get("authenticated_account")

        for sms in authenticated_account.sms_codes.all():
            sms.delete()

        if is_phone_used(data.get("phone")): # Verifica se o número está sendo usado por alguma conta
            raise serializers.ValidationError("an account with this phone number already exists")

        invalidate_expired_sms_codes(authenticated_account) # Invalida sms_codes expirados

        if authenticated_account.has_too_many_sms_codes(): # Verifica se a conta possui muitos códigos de sms ativos
            raise serializers.ValidationError("You have too many SMS codes. Please try again later")

        data["authenticated_account"] = authenticated_account
        return data

    def create(self, validated_data):
        authenticated_account = validated_data.get("authenticated_account")

        sms = SMSCode.objects.create( # Cria objeto SMSCode relacionado ao usuário logado
            account=authenticated_account,
        )

        send_sms_code( # Envia código de sms
            sms.code,
            validated_data.get("phone")
        )

        return SMSCode.code