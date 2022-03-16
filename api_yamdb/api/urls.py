from django.urls import include, path
from rest_framework import routers


from .views import CategoryViewSet, GenreViewSet, TitleViewSet

router = routers.SimpleRouter()
router.register('сategories', CategoryViewSet)
router.register('genres', GenreViewSet)
router.register('titles', TitleViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
urlpatterns = [path('v1/', include(urlpatterns))]