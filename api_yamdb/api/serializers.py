from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from rest_framework import serializers

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
    rating = serializers.IntegerField(read_only=True, default=None)

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'rating',
                  'description', 'genre', 'category', )
        read_only_fields = fields


class TitleEditSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(slug_field='slug',
                                            queryset=Category.objects.all())
    genre = serializers.SlugRelatedField(slug_field='slug',
                                         queryset=Genre.objects.all(),
                                         many=True)
    rating = serializers.IntegerField(read_only=True, default=None)

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description',
                  'genre', 'category', 'rating',)

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
    username = serializers.CharField(required=True)  # TODO: Не хватает ограничений, указанных в ТЗ
    email = serializers.EmailField(required=True)  # TODO: Аналогично

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError(
                'Нельзя создать пользователя с username = "me"')
        return value


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
            raise ValidationError(
                'Один автор, может оставить только один обзор на произведение')
        return data

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date',)
