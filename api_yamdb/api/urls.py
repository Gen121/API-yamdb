from django.urls import include, path
from rest_framework import routers

from .views import send_code, send_token, CategoryViewSet, CommentViewSet, GenreViewSet, ReviewViewSet, TitleViewSet, UserViewSet

router = routers.SimpleRouter()
router.register('categories', CategoryViewSet)
router.register('genres', GenreViewSet)
router.register('titles', TitleViewSet)
router.register('users', UserViewSet)
router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='reviews'
)
router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments'
)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/signup/', send_code),
    path('auth/token/', send_token),
]

urlpatterns = [path('v1/', include(urlpatterns))]
