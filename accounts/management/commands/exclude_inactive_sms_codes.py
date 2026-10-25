from django.core.management import BaseCommand
from accounts.models import SMSCode

class Command(BaseCommand):
    help = "Deleta objetos SMSCode inativos"

    def handle(self, *args, **options):

        SMSCode.objects.filter(
            active=False
        ).delete()