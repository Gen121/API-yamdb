from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = [
        ('USER', 'user'),
        ('MODERATOR', 'moderator'),
        ('ADMIN', 'admin'),
    ]
    email = models.EmailField(max_length=254, unique=True,
                              blank=False, null=False)
    first_name = models.CharField(max_length=150, blank=True)
    bio = models.TextField(blank=True)
    role = models.CharField(max_length=15, choices=ROLE_CHOICES,
                            default='USER', verbose_name='role')
    REQUIRED_FIELDS = ['username', 'email']
