from django.urls import include, path
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView

from .views import CategoryViewSet, GenreViewSet, TitleViewSet, UserViewSet

router = routers.SimpleRouter()
router.register('categories', CategoryViewSet)
router.register('genres', GenreViewSet)
router.register('titles', TitleViewSet)
router.register('users', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path(
        'auth/signup/', TokenObtainPairView.as_view(), name='token_obtain_pair'
    ),
]
urlpatterns = [path('v1/', include(urlpatterns))]
