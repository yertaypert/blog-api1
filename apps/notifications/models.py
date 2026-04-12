# Django modules
from django.db import models

# Project modules
from settings.base import AUTH_USER_MODEL
from django.contrib.auth import get_user_model
from apps.blog.models import Comment


User = AUTH_USER_MODEL


class Notification(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
    
    def __str__(self):
        return f"Notification for {self.recipient.email} on comment {self.comment.id}"