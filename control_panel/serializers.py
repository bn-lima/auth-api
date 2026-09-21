from rest_framework import serializers
from accounts.models import Account
from accounts.validators import PASSWORD_VALIDATOR

class AccountDetailSerializer(serializers.ModelSerializer): # Mostra os detalhes de uma conta
    account_id = serializers.SerializerMethodField()

    class Meta:
        model = Account
        fields = ("account_id", "email", "username", "profile", "cpf", "phone", "created_at", "is_staff")

    def get_account_id(self, obj):
        return int(obj.id)

class AccountsListSerializer(serializers.ModelSerializer): # Lista as contas
    account_id = serializers.SerializerMethodField()

    class Meta:
        model = Account
        fields = ("account_id", "username", "email", "profile")

    def get_account_id(self, obj): # Pega o id de cada conta
        return int(obj.id)

class DeleteAccountSerializer(serializers.Serializer): # Serializer responsável por deletar uma conta
    confirmation_password = serializers.CharField(required=True, max_length=128, write_only=True)

    def validate(self, data):
        authenticated_account = self.context.get("authenticated_account")
        #Verifica se a senha de confirmação está correta
        if not authenticated_account.check_password(data.get("confirmation_password")):
            raise serializers.ValidationError("invalid confirmation_password")

        return data

    def save(self, **kwargs):
        selected_account = self.context.get("selected_account") # Pega a conta que será deletada

        selected_account.delete() # Deleta a conta

        return True

class UpdateAccountSerializer(serializers.ModelSerializer): # Atualiza os dados de uma conta
    # Campo para confirmar a senha do usuário autenticado
    confirmation_password = serializers.CharField(required=True, max_length=128, write_only=True)

    class Meta:
        model = Account
        fields = ("username", "email", "profile", "confirmation_password", "cpf", "phone")

        extra_kwargs = { # Deixa os campos como não obrigatórios
            "username": {"required": False},
            "email": {"required": False},
            "profile": {"required": False}
        }

    def validate(self, data):
        authenticated_account = self.context.get("authenticated_account")
        # Verifica se a senha está correta
        if not authenticated_account.check_password(data.get("confirmation_password")):
            raise serializers.ValidationError("invalid confirmation_password")

        return data

class CreateAccountSerializer(serializers.ModelSerializer): # Cria conta pelo painel de controle
    confirmation_password = serializers.CharField(required=True, max_length=128, write_only=True) # Senha de confirmação do admin
    confirm_password = serializers.CharField(max_length=128, required=True, write_only=True, validators=[PASSWORD_VALIDATOR]) # Confirmar senha da conta que será criada

    class Meta:
        model = Account
        fields = (
            "email",
            "username",
            "profile",
            "cpf",
            "phone",
            "created_at",
            "is_staff",
            "confirmation_password",
            "password",
            "confirm_password",
        )

        extra_kwargs = { # Define validação de senha para o campo password
            "password": {
                "validators":[PASSWORD_VALIDATOR]
            }
        }

    def validate(self, data):
        authenticated_account = self.context.get("authenticated_account")
        # Verifica se a senha está correta
        if not authenticated_account.check_password(data.get("confirmation_password")):
            raise serializers.ValidationError("invalid confirmation_password")
        # Verifica se password e confirm_password estão iguais
        if data.get("password") != data.get("confirm_password"):
            raise serializers.ValidationError("passwords do not match")
 
        return data

    def create(self, validated_data):
        # Remove campos que não fazem parte do modelo
        password = validated_data.pop("password") # Password é removido para ser definido de forma segura na conta
        validated_data.pop("confirm_password")
        validated_data.pop("confirmation_password")

        account = Account.objects.create( # Cria objeto account sem senha
            **validated_data
        )

        account.set_password(password) # Define senha criptografada
        account.save()
        return account