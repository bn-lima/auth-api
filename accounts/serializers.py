from rest_framework import serializers
from .models import Account
from .validators import PASSWORD_VALIDATOR
from .services import authenticate_account, generate_account_tokens
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from .models import ResetPasswordToken
from .email import send_test_email

class RegisterAccountSerializer(serializers.ModelSerializer): # Serializer responsável por registrar usuário
    # Campo de confirmação de senha
    confirm_password = serializers.CharField(max_length=128, validators=[PASSWORD_VALIDATOR], write_only=True)

    class Meta:
        model = Account
        fields = ("username", "email", "password", "confirm_password", "profile")

        extra_kwargs = {
            "password": {
                "validators": [PASSWORD_VALIDATOR] # Define um validator no campo password
            }
        }

    def validate(self, data):
        if data.get("password") != data.get("confirm_password"): # Verifica se as senhas são iguais
            raise serializers.ValidationError("passwords do not match")

        return data

    def create(self, validated_data):   
        # Removo password e confirm_password dos dados validados
        password = validated_data.pop("password")
        validated_data.pop("confirm_password")

        account = Account.objects.create( # Cria usuário sem senha
            **validated_data
        )

        # Define senha de forma segura e salva o usuário criado
        account.set_password(password)
        account.save()

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

        if account.reset_password_tokens.filter( # Verifica se a conta possui 3 tokens de reset ativos
            active=True,
            expired=False
        ).count() >=3:

            raise serializers.ValidationError("You have reached the limit of 3 active password reset requests")

        data["account"] = account # Adiciona account nos dados validados
        return data

    def create(self, validated_data):
        account = self.validated_data.get("account")

        reset_token = ResetPasswordToken.objects.create(account=account) # Cria objeto reset token
        send_test_email(account.email, reset_token.key) # Envia email de recuperação

        return reset_token
