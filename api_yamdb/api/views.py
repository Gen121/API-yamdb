import django_filters
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend, FilterSet
from rest_framework import filters, mixins, pagination, status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.exceptions import ParseError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from reviews.models import Category, Genre, Review, Title, User
from .permissions import (Admin, AdminModeratorAuthorPermission,
                          AdminOrReadOnnly)
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, ReviewSerializer,
                          SendCodeSerializer, SendTokenSerializer,
                          TitleEditSerializer, UserMeSerializer,
                          UserSerializer)


class CategoryViewSet(mixins.CreateModelMixin,
                      mixins.ListModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet,):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    lookup_field = 'slug'
    permission_classes = (AdminOrReadOnnly, )
    filter_backends = (filters.SearchFilter, )
    search_fields = ('name', )


class GenreViewSet(mixins.CreateModelMixin,
                   mixins.ListModelMixin,
                   mixins.DestroyModelMixin,
                   viewsets.GenericViewSet, ):
# TODO:  Взгляните на эти два класса, сколько в них похожего
# Стоит вынести все повторяющиеся моменты в отдельный родительский класс

    serializer_class = GenreSerializer
    queryset = Genre.objects.all()
    lookup_field = 'slug'
    permission_classes = (AdminOrReadOnnly, )
    filter_backends = (filters.SearchFilter, )
    search_fields = ('name', )


class TitleFilter(FilterSet):  # TODO:  Фильтры нужно вынести в filters.py
    genre = django_filters.CharFilter(field_name='genre__slug')
    category = django_filters.CharFilter(field_name='category__slug')
    year = django_filters.NumberFilter(field_name='year')
    name = django_filters.CharFilter(field_name='name',
                                     lookup_expr='icontains')

    class Meta:
        model = Title
        fields = ('name', 'year', 'genre', 'category')


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()  # TODO:
    # Вот здесь можно подсчитывать рейтинг в одну строку,
    # используя механизмы annotate и Avg, вот документация по этому поводу:
    # https://docs.djangoproject.com/en/3.1/topics/db/aggregation/#order-of-annotate-and-filter-clauses
    serializer_class = TitleEditSerializer
    permission_classes = (AdminOrReadOnnly, )
    filter_backends = (DjangoFilterBackend, )
    filterset_class = TitleFilter


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (Admin,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    pagination_class = pagination.PageNumberPagination
    lookup_field = 'username'

    @action(detail=False, permission_classes=(IsAuthenticated, ),
            methods=['get', 'patch'], url_path='me',
            serializer_class=UserMeSerializer)
    def get_or_patch_me(self, request):
        if request.method == 'GET':
            serializer = self.get_serializer(request.user, many=False)
            return Response(serializer.data)
        serializer = self.get_serializer(
            instance=request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


def yamdb_send_mail(confirmation_code, email):
    return send_mail(
        subject='Ваш код подтверждения на yambd.com',
        message=f'Ваш код подтверждения на yambd.com: {confirmation_code}',
        from_email=settings.EMAIL_YAMDB,
        recipient_list=[email],
    )


@api_view(['POST'])
def send_code(request):
    serializer = SendCodeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = request.data.get('username')
    email = request.data.get('email')
    user = User.objects.get_or_create(username=username, email=email)[0]
    confirmation_code = default_token_generator.make_token(user)
    yamdb_send_mail(confirmation_code, email)
    message = {'email': email, 'username': username}
    return Response(message, status=status.HTTP_200_OK)


@api_view(['POST'])
def send_token(request):
    serializer = SendTokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = request.data.get('username')
    token = serializer.data.get('confirmation_code')
    user = get_object_or_404(User, username=username)
    if default_token_generator.check_token(user, token):
        token = AccessToken.for_user(user)
        return Response({'token': f'{token}'}, status=status.HTTP_200_OK)
    return Response('Неверный код подтверждения',
                    status=status.HTTP_400_BAD_REQUEST)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (AdminModeratorAuthorPermission, )

    def get_queryset(self):
        review = get_object_or_404(
            Review,
            id=self.kwargs.get('review_id'))  # TODO:
        # Здесь и ниже необходимо проверить,
        # что ревью на верный тайтл. Это можно сделать с помощью указания
        # дополнительного параметра в выборке title__id
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(
            Review,
            id=self.kwargs.get('review_id'))
        serializer.save(author=self.request.user, review=review)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (AdminModeratorAuthorPermission, )
    pagination_class = pagination.PageNumberPagination

    def get_queryset(self):
        title = self.get_title()
        return title.reviews.all()

    def perform_create(self, serializer):
        title = self.get_title()
        review = Review.objects.filter(
            title=title, author=self.request.user).exists()
        if review:  # TODO: Нужно вынести логику валидации в сериализатор
            raise ParseError(
                'Один автор, может оставить только один обзор на произведение')
        serializer.save(author=self.request.user, title=title)

    def get_title(self):
        return get_object_or_404(Title, id=self.kwargs.get('title_id'))
