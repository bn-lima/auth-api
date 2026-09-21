from django.urls import path, include
from .views import AccountDetailView, AccountsListView, DeleteAccountView, UpdateAccountView, CreateAccountView

urlpatterns = [
    path("account/", include([
        path("list/", AccountsListView.as_view(), name="account_list"), # Lista as contas
        path("create/", CreateAccountView.as_view(), name="create_account"), # Cria conta
        
        path("<int:pk>/", include([
            path("detail/", AccountDetailView.as_view(), name="account_detail"), # Mostra os detalhes de uma conta
            path("delete/", DeleteAccountView.as_view(), name="delete_account"), # Deleta uma conta
            path("update/", UpdateAccountView.as_view(), name="update_account") # Atualiza os dados de uma conta
        ]))
    ]))
]