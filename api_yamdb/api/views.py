from django.shortcuts import get_object_or_404
from rest_framework import filters, pagination, permissions, viewsets, mixins

from reviews.models import Category, Genre, Title, User
from .serializers import (CategorySerializer, GenreSerializer, TitleSerializer,
                          UserSerializer)
from .permissions import Admin, AdminOrReadOnnly


class CategoryViewSet(mixins.CreateModelMixin,
                      mixins.ListModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet,):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    lookup_field = 'slug'
    pagination_class = pagination.PageNumberPagination
    permission_classes = (AdminOrReadOnnly)


class GenreViewSet(mixins.CreateModelMixin,
                   mixins.ListModelMixin,
                   mixins.DestroyModelMixin,
                   viewsets.GenericViewSet,):
    serializer_class = GenreSerializer
    queryset = Genre.objects.all()
    lookup_field = 'slug'
    pagination_class = pagination.PageNumberPagination
    permission_classes = (AdminOrReadOnnly)


class TitleViewSet(viewsets.ModelViewSet):
    serializer_class = TitleSerializer
    queryset = Title.objects.all()
    pagination_class = pagination.PageNumberPagination
    permission_classes = (AdminOrReadOnnly,)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (Admin,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('user__username',)
