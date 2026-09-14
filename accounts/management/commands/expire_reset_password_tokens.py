from django.core.management import BaseCommand
from accounts.models import ResetPasswordToken
from django.utils import timezone

class Command(BaseCommand):
    help = "Inativa tokens de reset de senha expirados"

    def handle(self, *args, **options):
        ResetPasswordToken.objects.filter(
            active=True,
            expired=False,
            expires_at__lte=timezone.now()
        ).update(
            active=False,
            expired=True
        )