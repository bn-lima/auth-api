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