from rest_framework.generics import RetrieveAPIView, ListAPIView, UpdateAPIView
from accounts.models import Account
from rest_framework import permissions, status
from .serializers import AccountDetailSerializer, AccountsListSerializer, DeleteAccountSerializer, UpdateAccountSerializer
from .filters import AccountsListFilterSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView
from rest_framework.response import Response

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

class DeleteAccountView(APIView): # Deleta uma conta específica
    permission_classes = [permissions.IsAdminUser]

    def delete(self, request, pk, *args, **kwargs):

        selected_account = Account.objects.filter(id=pk).first() # Busca a conta pelo id

        if not selected_account: # Retorna erro caso não encontre
            return Response({"detail": "account not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = DeleteAccountSerializer(
            data=request.data,
            context={
                "authenticated_account": request.user,
                "selected_account": selected_account
            }
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({"message": "account deleted successfully"}, status=status.HTTP_200_OK)

class UpdateAccountView(UpdateAPIView): # Atualiza os dados de uma conta
    permission_classes = [permissions.IsAdminUser]
    serializer_class = UpdateAccountSerializer
    queryset = Account.objects.all()

    def get_serializer(self, *args, **kwargs):

        kwargs["context"] = { # Adiciona context no serializer
            "authenticated_account":self.request.user
        }

        return super().get_serializer(*args, **kwargs)