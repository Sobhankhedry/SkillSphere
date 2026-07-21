from celery import shared_task

from .services import NotificationService


@shared_task
def send_notification_task(recipient_id, notification_type, title, message, sender_id=None, link=""):
    from django.contrib.auth import get_user_model

    User = get_user_model()
    try:
        recipient = User.objects.get(id=recipient_id)
        sender = User.objects.get(id=sender_id) if sender_id else None
        NotificationService.create_notification(
            recipient=recipient,
            notification_type=notification_type,
            title=title,
            message=message,
            sender=sender,
            link=link,
        )
    except User.DoesNotExist:
        pass
