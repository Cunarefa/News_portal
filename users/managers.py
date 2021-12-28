from datetime import datetime

from django.db import models


class InviteTokenManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status=True, exp_date__gt=datetime.now())
