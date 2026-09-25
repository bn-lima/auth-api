from django.core.management import BaseCommand
from accounts.models import PendingAccountRegistration
from django.utils import timezone

class Command(BaseCommand):
    help = "Deleta pedidos de registro expirados"

    def handle(self, *args, **options):

        PendingAccountRegistration.objects.filter(
            expires_at__lte=timezone.now()
        ).delete()