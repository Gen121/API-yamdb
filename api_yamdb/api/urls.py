from django.urls import include, path
from rest_framework import routers

from .views import send_code, send_token, CategoryViewSet, GenreViewSet, TitleViewSet, UserViewSet

router = routers.SimpleRouter()
router.register('categories', CategoryViewSet)
router.register('genres', GenreViewSet)
router.register('titles', TitleViewSet)
router.register('users', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/signup/', send_code),
    path('auth/token/', send_token),
]
urlpatterns = [path('v1/', include(urlpatterns))]
