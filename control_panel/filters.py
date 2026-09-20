from django_filters import FilterSet, filters
from accounts.models import Account

class AccountsListFilterSet(FilterSet): # Filtro para AccountsListView

    username = filters.CharFilter()
    email = filters.CharFilter()
    created_at = filters.DateTimeFilter()

    class Meta:
        model = Account
        fields = ("username", "email", "created_at")