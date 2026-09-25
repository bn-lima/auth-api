from django.core.management import BaseCommand
from accounts.models import PendingRegistrationToken
from django.utils import timezone

class Command(BaseCommand):
    help = "Invalida pending registration tokens expirados"

    def handle(self, *args, **options):

        PendingRegistrationToken.objects.filter(
            expires_at__lte=timezone.now(),
            active=True,
            expired=False
        ).update(active=False, expired=True)