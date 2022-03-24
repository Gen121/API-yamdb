import datetime as dt

from django.db.models import Avg
from rest_framework import serializers

from reviews.models import (Category, Comment, Genre, GenreTitle, Review,
                            Title, User)


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
        now_year = dt.date.today().year
        if now_year < value:  # TODO:  Снизу тоже хорошо бы ограничить :)
            raise serializers.ValidationError('Ошибка в годе произведения')
        return value

    def create(self, validated_data):  # TODO:  Лишний метод
        genres = validated_data.pop('genre')
        title = Title.objects.create(**validated_data)
        for genre in genres:
            GenreTitle.objects.create(
                genre=genre, title=title)
        return title

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
    username = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)

    def validate(self, data):
        incomming_user = data['username']
        incomming_mail = data['email']
        check_user = User.objects.filter(username=incomming_user)
        check_mail = User.objects.filter(email=incomming_mail)
        if check_user and not check_mail:
            raise serializers.ValidationError(
                'Пользователь с таким именем существует')
        if check_mail and not check_user:
            raise serializers.ValidationError(
                'Почтовый адрес уже существует')
        return data

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

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date',)
