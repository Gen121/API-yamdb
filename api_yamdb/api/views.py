from django.shortcuts import get_object_or_404
from rest_framework import filters, pagination, permissions, viewsets, mixins

from reviews.models import Category, Genre, Title
from .serializers import CategorySerializer, GenreSerializer, TitleSerializer
from .permissions import AdminOrReadOnnly


class CategoryViewSet(mixins.CreateModelMixin,
                      mixins.ListModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet,):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    pagination_class = pagination.PageNumberPagination
    permission_classes = (AdminOrReadOnnly,)


class GenreViewSet(mixins.CreateModelMixin,
                   mixins.ListModelMixin,
                   mixins.DestroyModelMixin,
                   viewsets.GenericViewSet,):
    serializer_class = GenreSerializer
    queryset = Genre.objects.all()
    pagination_class = pagination.PageNumberPagination
    permission_classes = (AdminOrReadOnnly,)


class TitleViewSet(viewsets.ModelViewSet):
    serializer_class = TitleSerializer
    queryset = Title.objects.all()
    pagination_class = pagination.PageNumberPagination
    permission_classes = (AdminOrReadOnnly,)

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
