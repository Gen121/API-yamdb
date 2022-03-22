import datetime as dt

from django.db.models import Avg
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

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
            return int(obj.reviews.aggregate(Avg('score'))['score__avg'] + 0.5)
        except:
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
        if now_year < value:
            raise serializers.ValidationError('Ошибка в годе произведения')
        return value

    def create(self, validated_data):
        genres = validated_data.pop('genre')
        title = Title.objects.create(**validated_data)
        for genre in genres:
            GenreTitle.objects.create(
                genre=genre, title=title)
        return title

    def to_representation(self, instance):
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
    #author = serializers.SlugRelatedField(slug_field='username')

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'score', 'pub_date', )


class ReviewSerializer(serializers.ModelSerializer):
    #author = serializers.SlugRelatedField(slug_field='username')

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'pub_date', )
