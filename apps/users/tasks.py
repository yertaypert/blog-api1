# Django modules
from django.core.mail import send_mail
from celery import shared_task

# Project modules
from settings.base import AUTH_USER_MODEL


@shared_task(
        autoretry_for=(Exception,),
        retry_backoff=True,
        max_retries=3,
)
def send_welcome_email(user_id: int):
    """
    Send welcome email after user registration

    Automatic entire are important because:
        - SMTP servers can have temp network issues, rate limits
        - Retrying ensures the welcome email is delivered without registration fail
    """
    User = AUTH_USER_MODEL
    user = User.objects.get(pk=user_id)

    try:
        send_mail(
            subject="Welcome to my blog!",
            message=f"Hi {user.username}!",
            from_email="no-reply@myblog.com",
            recipient_list=[user.email],
            fail_silently=False,
        )
    except User.DoesNotExist:
        return "User not found"