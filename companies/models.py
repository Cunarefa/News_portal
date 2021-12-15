from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin, AbstractUser
from django.db import models


class Company(models.Model):
    name = models.CharField(max_length=255)
    url = models.URLField(max_length=150, blank=True, null=True)
    address = models.CharField(max_length=500, blank=True, null=True)
    date_created = models.DateField()
    logo = models.ImageField(upload_to='logos/%Y/%m/%d/', blank=True, null=True)

    def __str__(self):
        return self.name














