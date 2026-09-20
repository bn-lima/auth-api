from django.shortcuts import render
from rest_framework.generics import RetrieveAPIView
from accounts.models import Account
from rest_framework import permissions
from .serializers import AccountDetailSerializer

class AccountDetailView(RetrieveAPIView): # Mostra os detalhes de uma conta
    permission_classes = [permissions.IsAdminUser]
    serializer_class = AccountDetailSerializer
    queryset = Account.objects.all()
