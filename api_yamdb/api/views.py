import random

from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, pagination, status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.exceptions import ParseError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from reviews.models import Category, Genre, Review, Title, User
from .filters import TitleFilter
from .permissions import (Admin, AdminModeratorAuthorPermission,
                          AdminOrReadOnnly)
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, ReviewSerializer,
                          SendCodeSerializer, SendTokenSerializer,
                          TitleEditSerializer, UserMeSerializer,
                          UserSerializer)


class CreateListDestroyViewSet(mixins.CreateModelMixin,
                               mixins.ListModelMixin,
                               mixins.DestroyModelMixin,
                               viewsets.GenericViewSet, ):
    lookup_field = 'slug'
    permission_classes = (AdminOrReadOnnly, )
    filter_backends = (filters.SearchFilter, )
    search_fields = ('name', )


class CategoryViewSet(CreateListDestroyViewSet):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()


class GenreViewSet(CreateListDestroyViewSet):
    serializer_class = GenreSerializer
    queryset = Genre.objects.all()


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
        else:  # TODO:  После return не нужен else
            serializer = self.get_serializer(
                instance=request.user, data=request.data, partial=True)
            if serializer.is_valid():  # TODO:
                # Стоит воспользоваться https://www.django-rest-framework.org/api-guide/exceptions/#validationerror
                # И избавиться от if и вложенного блока
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)


def yamdb_send_mail(confirmation_code, email):
    return send_mail(
        subject='Ваш код подтверждения на yambd.com',
        message=f'Ваш код подтверждения на yambd.com: {confirmation_code}',
        from_email='registration@yambd.com',  # TODO:  Почту стоит положить в settings.py
        recipient_list=[email],
    )


@api_view(['POST'])
def send_code(request):
    serializer = SendCodeSerializer(data=request.data)
    username = request.data.get('username')  # TODO:
    # Данные нужно доставать только из validated_data, после проверки валидности сериализатора
    email = request.data.get('email')
    if username == 'me':  # TODO: Эту валидацию стоит вынести в сериализатор
        message = 'Нельзя создать пользователя с username = "me"'
        return Response(message, status=status.HTTP_400_BAD_REQUEST)
    if serializer.is_valid():  # TODO: См. выше про raise_exception
        confirmation_code = str(random.randrange(1, 999999))  # TODO:
        # Для создания кода подтверждения нужно использовать стандартные механизмы, это надёжнее и безопаснее
        # https://docs.djangoproject.com/en/3.1/topics/auth/default/#django.contrib.auth.views.PasswordResetView
        # https://github.com/django/django/blob/master/django/contrib/auth/tokens.py#L107a
        user = User.objects.filter(username=username, email=email).exists()
        if not user:
            User.objects.create(  # TODO: Можно упростить код и воспользоваться get_or_create
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
    if serializer.is_valid():  # TODO: См. выше про raise_exception
        username = request.data.get('username')  # TODO: Данные достаём только отвалидированные
        confirmation_code = serializer.data.get('confirmation_code')
        user = get_object_or_404(User, username=username)
        if confirmation_code == user.confirmation_code:  # TODO:
            # Лучше пользоваться стандартным механизмом
            # https://www.programcreek.com/python/example/99849/django.contrib.auth.tokens.default_token_generator.check_token
            token = AccessToken.for_user(user)
            return Response({'token': f'{token}'}, status=status.HTTP_200_OK)
        return Response('Неверный код подтверждения',
                        status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (AdminModeratorAuthorPermission, )

    def get_queryset(self):
        review = get_object_or_404(
            Review,
            id=self.kwargs.get('review_id'),
            title=self.kwargs.get('title_id'))
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(
            Review,
            id=self.kwargs.get('review_id'),
            title=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, review=review)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (AdminModeratorAuthorPermission,)
    
    def get_queryset(self):
        title = get_object_or_404(Title, id=self.kwargs.get("title_id"))
        return title.reviews.all()
    
    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs.get("title_id"))
        serializer.save(author=self.request.user, title=title)

    def get_title(self):
        return get_object_or_404(Title, id=self.kwargs.get('title_id'))
