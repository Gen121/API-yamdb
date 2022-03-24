from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from reviews.models import (Category, Comment, Genre,
                            QUATERNARY_GEOLOGICAL_PERIOD, Review, Title,
                            TODAYS_YEAR, User)


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ('name', 'slug', )


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        fields = ('name', 'slug', )


class TitleSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(many=True, read_only=True)
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'rating',
                  'description', 'genre', 'category', )

    def get_rating(self, obj):
        try:
            return int(obj.reviews.aggregate(Avg('score'))['score__avg'] + 0.5)  # TODO: Не самое лучшее решение, будет пересчитываться на каждый запрос, покажу во вьюхе
        except Exception:
            return None


class TitleEditSerializer(TitleSerializer):
    category = serializers.SlugRelatedField(slug_field='slug',
                                            queryset=Category.objects.all())
    genre = serializers.SlugRelatedField(slug_field='slug',
                                         queryset=Genre.objects.all(),
                                         many=True)
    description = serializers.CharField(required=False)

    class Meta:
        model = Title
        fields = ('name', 'year', 'description', 'genre', 'category', )

    def validate_year(self, value):
        now_year = TODAYS_YEAR
        if now_year < value:
            raise serializers.ValidationError(
                'Невозможна публикация будущих произведений')
        if value < QUATERNARY_GEOLOGICAL_PERIOD:
            raise serializers.ValidationError(
                ' Ограничение для прошлого - антропоген (2,588 млн. лет назад)'
            )
        return value

    def to_representation(self, instance):  # TODO:  Лишний метод
        serializer = TitleSerializer(instance)
        return serializer.data


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role',)
        model = User


class UserMeSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role',)
        model = User
        read_only_fields = ('role',)


class SendCodeSerializer(serializers.Serializer):
    username = serializers.CharField(
        required=True,
        validators=[UniqueValidator(
            # TODO: Не очень хорошее решение.
            # Представьте ситуацию:
            # 1) Пользователь отправил мейл и юзернейм
            # 2) Система отдала ему письмо с токеном и создала пользователя в базе с таким емейлом и юзернеймом
            # 3) Пользователь потерял письмо
            # 4) Пытается отправить ещё раз - а сервер ему ничего не возвращает, потому что такой емейл уже есть в базе
            # Нужно это обдумать и решить, валидацию на это в сериализаторе стоит удалить.
            # В качестве родительского класса нужно брать обычный сериализатор, во вьюхе использовать get_or_create
            queryset=User.objects.all(),
            message='Пользователь с таким именем уже зарегистрирован')])
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(
            queryset=User.objects.all(),
            message='Почтовый адрес уже зарегистрирован')])


class SendTokenSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field='username'
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date',)


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field='username'
    )

    def validate(self, data):
        request = self.context['request']
        author = request.user
        title_id = self.context.get('view').kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        if (
            request.method == "POST"
            and Review.objects.filter(title=title, author=author).exists()
        ):
            raise ValidationError('Один автор, может оставить только один обзор на произведение')
        return data
    
    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date',)
