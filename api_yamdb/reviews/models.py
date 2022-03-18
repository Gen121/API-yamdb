from django.contrib.auth.models import AbstractUser
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=50, unique=True)


class Genre(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=50, unique=True)


class Title(models.Model):
    name = models.CharField(max_length=256)
    year = models.IntegerField()
    rating = models.IntegerField(null=True)
    description = models.TextField(
        blank=True)
    genre = models.ManyToManyField(
        'Genre',
        through='GenreTitle',
        blank=True,
        null=True, )
    category = models.ForeignKey(
        'Category',
        on_delete=models.SET_NULL,
        related_name='titles',
        blank=True,
        null=True, )


class GenreTitle(models.Model):
    genre = models.ForeignKey(Genre,
                              related_name='titles',
                              on_delete=models.CASCADE)
    title = models.ForeignKey(Title, on_delete=models.CASCADE)


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
