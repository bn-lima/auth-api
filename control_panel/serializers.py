from rest_framework import serializers
from accounts.models import Account

class AccountDetailSerializer(serializers.ModelSerializer): # Mostra os detalhes de uma conta
    account_id = serializers.SerializerMethodField()

    class Meta:
        model = Account
        fields = ("account_id", "email", "username", "profile", "created_at", "is_staff")

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
        fields = ("username", "email", "profile", "confirmation_password")

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