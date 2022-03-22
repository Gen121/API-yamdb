import datetime as dt

from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from reviews.models import Category, Genre, GenreTitle, Title, User


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
            return obj.reviews.aggregate(Avg('score'))['score__avg']
        except:
            return 0

    # def validate_year(self, value):
    #     now_year = dt.date.today().year
    #     if now_year < value:
    #         raise serializers.ValidationError('Ошибка в годе произведения')
    #     return value

    # def validate_category(self, value):
    #     if type(value) != str:
    #         raise serializers.ValidationError(
    #             'Категория дожна быть передана в виде строки')
    #     if value not in Category.objects.values_list('slug', flat=True):
    #         raise serializers.ValidationError(
    #             f'Категории <{value}>, нет в базе данных.')
    #     return value

    # def validate_genre(self, value):
    #     if type(value) != list:
    #         raise serializers.ValidationError(
    #             'Жанры дожны быть переданы в виде массива [<genre_1>,'
    #             '<genre_2>, ... <genre_n>]')
    #     for genre in value:
    #         if genre not in Genre.objects.values_list('slug', flat=True):
    #             raise serializers.ValidationError(
    #                 f'Жанр <{genre}>, нет в базе данных.')
    #     return value

    # def create(self, validated_data):
    #     genres = validated_data.pop('genre')
    #     category = validated_data.pop('category')
    #     category = Category.objects.get(slug=category)
    #     title = Title.objects.create(**validated_data, category=category)
    #     genre_list = [Genre.objects.get(slug=i) for i in genres]
    #     for genre in genre_list:
    #         GenreTitle.objects.create(
    #             genre=genre, title=title)
    #     return title


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
