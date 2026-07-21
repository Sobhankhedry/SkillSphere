import logging

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from apps.search.indexing import delete_project, index_project

from .models import Project

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Project)
def project_post_save(sender, instance, **kwargs):
    try:
        index_project(instance)
    except Exception as e:
        logger.error("Failed to index project %s: %s", instance.id, e)


@receiver(post_delete, sender=Project)
def project_post_delete(sender, instance, **kwargs):
    try:
        delete_project(instance.id)
    except Exception as e:
        logger.error("Failed to delete project %s from ES: %s", instance.id, e)
