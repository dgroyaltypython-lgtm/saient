from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import StaffProfile


@receiver(post_save, sender=get_user_model())
def create_staff_profile(sender, instance, created, **kwargs):
    # Profiles are intentionally not auto-created because the office must
    # be selected by an administrator.
    return
