from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from rest_framework import filters, pagination, permissions, status, viewsets, mixins
from rest_framework.decorators import action, api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

import random

from reviews.models import Category, Genre, Title, User
from .serializers import (CategorySerializer, GenreSerializer,
                          SendCodeSerializer, SendTokenSerializer,
                          TitleSerializer, UserMeSerializer, UserSerializer)
from .permissions import Admin, AdminOrReadOnnly


class CategoryViewSet(mixins.CreateModelMixin,
                      mixins.ListModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet,):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    lookup_field = 'slug'
    pagination_class = pagination.PageNumberPagination
    permission_classes = (AdminOrReadOnnly,)


class GenreViewSet(mixins.CreateModelMixin,
                   mixins.ListModelMixin,
                   mixins.DestroyModelMixin,
                   viewsets.GenericViewSet,):
    serializer_class = GenreSerializer
    queryset = Genre.objects.all()
    lookup_field = 'slug'
    pagination_class = pagination.PageNumberPagination
    permission_classes = (AdminOrReadOnnly,)


class TitleViewSet(viewsets.ModelViewSet):
    serializer_class = TitleSerializer
    queryset = Title.objects.all()
    pagination_class = pagination.PageNumberPagination
    permission_classes = (AdminOrReadOnnly,)

    def perform_create(self, serializer):
        category_data = self.request.data['category']
        category = get_object_or_404(Category, slug=category_data)
        genre_data = self.request.data['genre']
        genre_list = [get_object_or_404(Genre, slug=i) for i in genre_data]

        serializer.save(
            category=category,
            genre=genre_list)


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
    send_mail(
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
        user = User.objects.filter(username=username).exists()
        mail = User.objects.filter(email=email).exists()
        if not user and not mail:
            User.objects.create(username=username, email=email)
            yamdb_send_mail(confirmation_code, email)
            message = {'email': email, 'username': username}
            return Response(message, status=status.HTTP_200_OK)
        if user and mail:
            User.objects.filter(username=username).update(
                confirmation_code=confirmation_code
            )
            yamdb_send_mail(confirmation_code, email)
            message = {'email': email, 'username': username}
            return Response(message, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
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
