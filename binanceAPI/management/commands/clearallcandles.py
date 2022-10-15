from django.core.management.base import BaseCommand
from binanceAPI.models import KlineIndicatorModel

class Command(BaseCommand):
    def handle(self, *args, **options):
        kims = KlineIndicatorModel.objects.all()
        kims.delete()
        



