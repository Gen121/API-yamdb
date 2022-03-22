import django_filters
from django_filters.rest_framework import DjangoFilterBackend, FilterSet
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from rest_framework import filters, pagination, status, viewsets, mixins
from rest_framework.decorators import action, api_view
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

import random

from reviews.models import Category, Genre, Title, User, Review
from .serializers import (CategorySerializer, GenreSerializer,
                          SendCodeSerializer, SendTokenSerializer,
                          TitleEditSerializer, TitleSerializer,
                          UserMeSerializer, UserSerializer,
                          CommentSerializer, ReviewSerializer)
from .permissions import Admin, AdminOrReadOnnly, AdminModeratorAuthorPermission


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
    serializer_class = GenreSerializer
    queryset = Genre.objects.all()
    lookup_field = 'slug'
    permission_classes = (AdminOrReadOnnly, )
    filter_backends = (filters.SearchFilter, )
    search_fields = ('name', )


class TitleFilter(FilterSet):
    genre = django_filters.CharFilter(field_name='genre__slug')
    category = django_filters.CharFilter(field_name='category__slug')
    year = django_filters.NumberFilter(field_name='year')
    name = django_filters.CharFilter(field_name='name',
                                     lookup_expr='icontains')

    class Meta:
        model = Title
        fields = ('name', 'year', 'genre', 'category')


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    permission_classes = (AdminOrReadOnnly, )
    filter_backends = (DjangoFilterBackend, )
    filterset_class = TitleFilter

    def get_object(self):
        return get_object_or_404(Title, pk=self.kwargs.get('pk'))

    def get_serializer_class(self):
        if self.action in ('create', 'partial_update', 'update'):
            return TitleEditSerializer
        else:
            return TitleSerializer


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
        else:
            serializer = self.get_serializer(
                instance=request.user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)


def yamdb_send_mail(confirmation_code, email):
    return send_mail(
        subject='Ваш код подтверждения на yambd.com',
        message=f'Ваш код подтверждения на yambd.com: {confirmation_code}',
        from_email='registration@yambd.com',
        recipient_list=[email],
    )


@api_view(['POST'])
def send_code(request):
    serializer = SendCodeSerializer(data=request.data)
    username = request.data.get('username')
    email = request.data.get('email')
    if username == 'me':
        message = 'Нельзя создать пользователя с username = "me"'
        return Response(message, status=status.HTTP_400_BAD_REQUEST)
    if serializer.is_valid():
        confirmation_code = str(random.randrange(1, 999999))
        user = User.objects.filter(username=username, email=email).exists()
        if not user:
            User.objects.create(
                username=username,
                email=email, confirmation_code=confirmation_code)
            yamdb_send_mail(confirmation_code, email)
            message = {'email': email, 'username': username}
            return Response(message, status=status.HTTP_200_OK)
        User.objects.filter(email=email).update(
            confirmation_code=confirmation_code
        )
        yamdb_send_mail(confirmation_code, email)
        message = {'email': email, 'username': username}
        return Response(message, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def send_token(request):
    serializer = SendTokenSerializer(data=request.data)
    if serializer.is_valid():
        username = request.data.get('username')
        confirmation_code = serializer.data.get('confirmation_code')
        user = get_object_or_404(User, username=username)
        if confirmation_code == user.confirmation_code:
            token = AccessToken.for_user(user)
            return Response({'token': f'{token}'}, status=status.HTTP_200_OK)
        return Response('Неверный код подтверждения',
                        status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (AdminModeratorAuthorPermission, )
    #permission_classes = (AdminModeratorAuthorPermission,)IsAuthenticatedOrReadOnly

    def get_queryset(self):
        review = get_object_or_404(
            Review,
            id=self.kwargs.get('review_id'))
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(
            Review,
            id=self.kwargs.get('review_id'))
        serializer.save(author=self.request.user, review=review)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, AdminModeratorAuthorPermission)
    #permission_classes = (AdminModeratorAuthorPermission,)

    def get_queryset(self):
        title = get_object_or_404(
            Title,
            id=self.kwargs.get('title_id'))
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(
            Title,
            id=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)
