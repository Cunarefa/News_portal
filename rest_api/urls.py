from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_bulk.routes import BulkRouter

from .views import LoginView, UserViewset, CompanyViewSet, PostViewSet, PostBulkUpdate

router = DefaultRouter()
bulk_router = BulkRouter()

router.register('users', UserViewset, basename='users')
router.register('companies', CompanyViewSet, basename='companies')
router.register('posts', PostViewSet, basename='posts')
router.register('posts/<int:pk>', PostViewSet, basename='posts')
bulk_router.register('posts/multiple', PostBulkUpdate, basename='bulk_posts')

urlpatterns = [
    path('login', LoginView.as_view(), name='login'),
    # path('mail', index)
]

urlpatterns += bulk_router.urls
urlpatterns += router.urls
