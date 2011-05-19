from datetime import datetime
from django.core.management.base import BaseCommand
from sentinel.models import Address, GREY
from sentinel.utils import remove_addresses

class Command(BaseCommand):
    def handle(self, days='90', max_offences=3, **options):
        cutoff = datetime.now() - timedelta(days=int(days))
        qs = Address.objects.filter(flag=GREY, updated__lt=cutoff, count__lte=max_offences)
        remove_addresses(qs)
