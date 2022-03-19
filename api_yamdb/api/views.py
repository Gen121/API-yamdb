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
    permission_classes = (AdminOrReadOnnly, )


class GenreViewSet(mixins.CreateModelMixin,
                   mixins.ListModelMixin,
                   mixins.DestroyModelMixin,
                   viewsets.GenericViewSet, ):
    serializer_class = GenreSerializer
    queryset = Genre.objects.all()
    lookup_field = 'slug'
    pagination_class = pagination.PageNumberPagination
    permission_classes = (AdminOrReadOnnly, )


class TitleViewSet(viewsets.ModelViewSet):
    serializer_class = TitleSerializer
    queryset = Title.objects.all()
    pagination_class = pagination.PageNumberPagination
    permission_classes = (AdminOrReadOnnly, )

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
    permission_classes = (Admin, )
    filter_backends = (filters.SearchFilter, )
    search_fields = ('user__username', )
