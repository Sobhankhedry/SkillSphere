import logging

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from apps.search.indexing import delete_user, index_user

from .models import User

logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def user_post_save(sender, instance, **kwargs):
    try:
        index_user(instance)
    except Exception as e:
        logger.error("Failed to index user %s: %s", instance.id, e)


@receiver(post_delete, sender=User)
def user_post_delete(sender, instance, **kwargs):
    try:
        delete_user(instance.id)
    except Exception as e:
        logger.error("Failed to delete user %s from ES: %s", instance.id, e)
