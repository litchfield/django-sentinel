from django.dispatch import receiver
from django.db.models.signals import *
from models import Address
from flags import load_flags, delete_flags

@receiver(pre_save, sender=Address)
def save_address(sender, instance, *args, **kwargs):
    load_flags([instance])

@receiver(pre_delete, sender=Address)
def delete_address(sender, instance, *args, **kwargs):
    delete_flags([instance])
