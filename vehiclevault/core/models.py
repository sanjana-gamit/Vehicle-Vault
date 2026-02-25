from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid


User = settings.AUTH_USER_MODEL


# =========================
# BASE MODEL (DRY + CLEAN)
# =========================
class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


