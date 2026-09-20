from django.urls import path, include
from .views import AccountDetailView, AccountsListView, DeleteAccountView

urlpatterns = [
    path("account/", include([
        path("list/", AccountsListView.as_view(), name="account_list"), # Lista as contas
        
        path("<int:pk>/", include([
            path("detail/", AccountDetailView.as_view(), name="account_detail"), # Mostra os detalhes de uma conta
            path("delete/", DeleteAccountView.as_view(), name="delete_account") # Deleta uma conta
        ]))
    ]))
]