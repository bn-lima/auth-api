from django.urls import path, include
from .views import AccountDetailView, AccountsListView

urlpatterns = [
    path("account/", include([
        path("list/", AccountsListView.as_view(), name="account_list"), # Lista as contas
        
        path("<int:pk>/", include([
            path("detail/", AccountDetailView.as_view(), name="account_detail") # Mostra os detalhes de uma conta
        ]))
    ]))
]