import datetime as dt

from django.contrib.auth.models import AbstractUser
from django.core.validators import (MinValueValidator,
                                    MaxValueValidator,
                                    RegexValidator)
from django.db import models


QUATERNARY_GEOLOGICAL_PERIOD = -2588000
TODAYS_YEAR = dt.date.today().year
MAX_SCORE = 10
MIN_SCORE = 1


class Category(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=50,
                            unique=True,
                            validators=[RegexValidator(
                                regex=r'^[-a-zA-Z0-9_]+$',
                                message='Ошибка валидации поля slug')])

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Genre(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=50,
                            unique=True,
                            validators=[RegexValidator(
                                regex=r'^[-a-zA-Z0-9_]+$',
                                message='Ошибка валидации поля slug')])

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class Title(models.Model):
    name = models.CharField(max_length=256)
    year = models.IntegerField(validators=(
        MinValueValidator(QUATERNARY_GEOLOGICAL_PERIOD),
        MaxValueValidator(TODAYS_YEAR)))
    description = models.TextField(
        blank=True)
    genre = models.ManyToManyField(
        'Genre',
        through='GenreTitle',
        blank=True, )
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

RoleChoises(models.TEXt):
    _user = 'user'
    _admin = 'admin'
    _moderator = 'moderator'
    
    d

class User(AbstractUser):
    ROLE_CHOICES = [
        ('user', 'user'),
        ('moderator', 'moderator'),
        ('admin', 'admin'),
    ]  # TODO: Не хватает явного указания поля username
    email = models.EmailField(max_length=254, unique=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    bio = models.TextField(blank=True)
    role = models.Choices CharField(max_length=len(max(ROLE_CHOICES)),  # TODO: В ROLE_CHOICES лежат кортежи, 
                            choices=ROLE_CHOICES,  # так что максимальная длина будет - 2, нужно искать максимальную длину самих строк
                            default='user', verbose_name='role')

    @property
    def is_admin(self):
        return self.role == 'admin'  # TODO: Тут роль сравнивается с обычной строкой, это не очень хорошо
# Сперва нужно сделать отдельный класс, где будут в качестве полей все нужные роли, потом к ним обращаться по имени поля
# А вот там где объявлено ROLES вместо строк использовать значения из ранее созданного класса

    @property
    def is_moderator(self):
        return self.role == 'moderator'


class Review(models.Model):
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Произведение'
    )

    text = models.TextField(
        verbose_name='Текст отзыва'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор отзыва',
        db_index=True
    )
    score = models.IntegerField(
        verbose_name='Оценка',
        validators=(
            MinValueValidator(MIN_SCORE),
            MaxValueValidator(MAX_SCORE)
        ),
        error_messages={'validators': 'Оценка должна быть от 1 до 10'}
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации отзыва',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(
                fields=('author', 'title'),
                name='unique_review'
            )]
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text


class Comment(models.Model):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='comments',
        verbose_name='Отзыв'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор комментария',
        db_index=True
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата добавления комментария',
        auto_now_add=True,
        db_index=True
    )
    text = models.TextField(
        verbose_name='Текст комментария',
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text
