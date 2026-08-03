from django.contrib.auth import get_user_model

from .models import Feedback, Notification

User = get_user_model()


class NotificationService:
    @staticmethod
    def create_notification(
        recipient: User,
        notification_type: str,
        title: str,
        message: str,
        sender: User | None = None,
        link: str = "",
    ) -> Notification:
        notification = Notification.objects.create(
            recipient=recipient,
            sender=sender,
            notification_type=notification_type,
            title=title,
            message=message,
            link=link,
        )
        NotificationService._send_realtime_notification(notification)
        return notification

    @staticmethod
    def _send_realtime_notification(notification: Notification) -> None:
        try:
            from channels.layers import get_channel_layer
            from asgiref.sync import async_to_sync

            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"user_{notification.recipient.id}",
                {
                    "type": "notification.send",
                    "notification": {
                        "id": str(notification.id),
                        "type": notification.notification_type,
                        "title": notification.title,
                        "message": notification.message,
                        "link": notification.link,
                        "created_at": notification.created_at.isoformat(),
                    },
                },
            )
        except Exception:
            pass

    @staticmethod
    def mark_as_read(notification_id: str, user: User) -> bool:
        try:
            notification = Notification.objects.get(id=notification_id, recipient=user)
            notification.mark_read()
            return True
        except Notification.DoesNotExist:
            return False

    @staticmethod
    def mark_all_read(user: User) -> int:
        return Notification.objects.filter(recipient=user, is_read=False).update(
            is_read=True
        )

    @staticmethod
    def get_user_notifications(user: User, unread_only: bool = False):
        queryset = Notification.objects.filter(recipient=user)
        if unread_only:
            queryset = queryset.filter(is_read=False)
        return queryset

    @staticmethod
    def get_unread_count(user: User) -> int:
        return Notification.objects.filter(recipient=user, is_read=False).count()


class FeedbackService:
    @staticmethod
    def create_feedback(
        user: User,
        severity: str,
        title: str,
        message: str,
        action: str = "",
    ) -> Feedback:
        return Feedback.objects.create(
            user=user,
            severity=severity,
            title=title,
            message=message,
            action=action,
        )

    @staticmethod
    def get_user_feedbacks(user: User, unread_only: bool = False):
        queryset = Feedback.objects.filter(user=user)
        if unread_only:
            queryset = queryset.filter(is_read=False)
        return queryset

    @staticmethod
    def mark_as_read(feedback_id: str, user: User) -> bool:
        try:
            feedback = Feedback.objects.get(id=feedback_id, user=user)
            feedback.mark_read()
            return True
        except Feedback.DoesNotExist:
            return False

    @staticmethod
    def mark_all_read(user: User) -> int:
        return Feedback.objects.filter(user=user, is_read=False).update(is_read=True)

    @staticmethod
    def get_unread_count(user: User) -> int:
        return Feedback.objects.filter(user=user, is_read=False).count()

    @staticmethod
    def success(user: User, title: str, message: str, action: str = "") -> Feedback:
        return FeedbackService.create_feedback(user, "success", title, message, action)

    @staticmethod
    def error(user: User, title: str, message: str, action: str = "") -> Feedback:
        return FeedbackService.create_feedback(user, "error", title, message, action)

    @staticmethod
    def warning(user: User, title: str, message: str, action: str = "") -> Feedback:
        return FeedbackService.create_feedback(user, "warning", title, message, action)

    @staticmethod
    def info(user: User, title: str, message: str, action: str = "") -> Feedback:
        return FeedbackService.create_feedback(user, "info", title, message, action)
