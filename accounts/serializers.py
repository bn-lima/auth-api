from rest_framework import serializers
from .models import Account
from .validators import PASSWORD_VALIDATOR

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