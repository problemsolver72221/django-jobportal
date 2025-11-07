from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import CustomUser, Profile


@receiver(post_save, sender=CustomUser)
def create_or_update_profile(sender, instance, created, **kwargs):
    print(
        sender,
        "sender",
        instance,
        "instance",
        created,
        "created",
    )
    if created:
        Profile.objects.create(user=instance)
    else:
        Profile.objects.get_or_create(user=instance)
