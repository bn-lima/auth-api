from django.core.management import BaseCommand
from accounts.models import AccountDeletionToken
from django.utils import timezone

class Command(BaseCommand):
    help = "Desativa tokens de exclusão de conta expirados"

    def handle(self, *args, **options):

        AccountDeletionToken.objects.filter(
            active=True,
            expired=False,
            expires_at__lte=timezone.now()
        ).update(
            expired=True,
            active=False
        )