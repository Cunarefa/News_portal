from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import LoginView, UserViewset, CompanyViewSet, PostViewSet, PostBulkUpdate

router = DefaultRouter()

router.register('users', UserViewset, basename='users')
router.register('companies', CompanyViewSet, basename='companies')
router.register('posts', PostViewSet, basename='posts')
router.register('posts/<int:pk>', PostViewSet, basename='posts')
router.register('posts/multiple', PostBulkUpdate, basename='bulk_posts')

urlpatterns = [
    path('login', LoginView.as_view(), name='login'),
]

urlpatterns += router.urls

