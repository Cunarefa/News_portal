from rest_framework.routers import DefaultRouter
from rest_framework_bulk.routes import BulkRouter

from posts.views import PostViewSet, PostBulkUpdate

router = DefaultRouter()
bulk_router = BulkRouter()

router.register('posts', PostViewSet, basename='posts')
router.register('posts/<int:pk>', PostViewSet, basename='posts')
bulk_router.register('posts/multiple', PostBulkUpdate, basename='bulk_posts')

urlpatterns = router.urls
