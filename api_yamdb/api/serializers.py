from rest_framework import serializers

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

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'rating',
                  'description', 'genre', 'category', )

    def validate_category(self, value):
        if type(value) != str:
            raise serializers.ValidationError(
                'Категория дожна быть передана в виде строки')

    def validate_genre(self, value):
        if type(value) != list:
            raise serializers.ValidationError(
                'Жанры дожны быть переданы в виде массива [<genre_1>,'
                '<genre_2>, ... <genre_n>]')
        for genre in value:
            if genre not in Genre.objects.all.values():
                raise serializers.ValidationError(
                    f'Жанр {genre}, не зарегистрирован в базе данных.')

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
    username = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)


class SendTokenSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)
