from django.db import models


class Title(models.Model):
    name = models.CharField(max_length=256)
    year = models.IntegerField()
    rating = models.IntegerField()
    description = models.TextField(
        null=True,
        blank=True)
    genre = models.ManyToManyField(
        'Genre',
        related_name='title', )
    category = models.ForeignKey(
        'Category',
        on_delete=models.SET_NULL,
        related_name='titles',
        null=True, )


class Category(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=50, unique=True)

class Genre(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=50, unique=True)