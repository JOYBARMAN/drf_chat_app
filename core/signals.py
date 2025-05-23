from django.db.models.signals import post_save
from django.dispatch import receiver

from core.models import User, UserProfile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Signal to create a UserProfile instance when a User is created."""
    if created:
        UserProfile.objects.get_or_create(user=instance)