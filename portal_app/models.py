from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin, AbstractUser
from django.db import models


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, user_type=None, **extra_fields):
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.user_type = user_type
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(email, password, user_type='Superuser', **extra_fields)


class User(AbstractUser):
    username = None
    email = models.EmailField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=24, blank=True, null=True)
    avatar = models.ImageField(upload_to='photos/%Y/%m/%d/', blank=True, null=True)
    ROLES = (
        ('Superuser', 'superuser'),
        ('Admin', 'admin'),
        ('Client', 'client'),
    )
    user_type = models.CharField(choices=ROLES, default='Client', max_length=10)
    company = models.ForeignKey('Company', on_delete=models.SET_NULL, related_name='users', null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'


class Company(models.Model):
    name = models.CharField(max_length=255)
    url = models.URLField(max_length=150, blank=True, null=True)
    address = models.CharField(max_length=500, blank=True, null=True)
    date_created = models.DateField()
    logo = models.ImageField(upload_to='logos/%Y/%m/%d/', blank=True, null=True)

    def __str__(self):
        return self.name


class Post(models.Model):
    title = models.CharField(max_length=500)
    text = models.TextField(max_length=1000, blank=True, null=True)
    TOPIC_TYPES = (
        ('nature', 'Nature'),
        ('sport', 'Sport'),
        ('art', 'Art'),
        ('travel', 'Travel')
    )
    topic = models.CharField(choices=TOPIC_TYPES, max_length=6)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')

    def __str__(self):
        return self.title









