from rest_framework.generics import RetrieveAPIView, ListAPIView
from accounts.models import Account
from rest_framework import permissions
from .serializers import AccountDetailSerializer, AccountsListSerializer
from .filters import AccountsListFilterSet
from django_filters.rest_framework import DjangoFilterBackend

class AccountsListView(ListAPIView): # Lista as contas
    permission_classes = [permissions.IsAdminUser]
    queryset = Account.objects.all()
    serializer_class = AccountsListSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = AccountsListFilterSet

class AccountDetailView(RetrieveAPIView): # Mostra os detalhes de uma conta
    permission_classes = [permissions.IsAdminUser]
    serializer_class = AccountDetailSerializer
    queryset = Account.objects.all()