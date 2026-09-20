from django.urls import path, include
from .views import AccountDetailView

urlpatterns = [
    path("account/", include([
        path("<int:pk>/", include([
            path("detail/", AccountDetailView.as_view(), name="account_detail") # Mostra os detalhes de uma conta
        ]))
    ]))
]