from rest_framework.routers import DefaultRouter

from companies.views import CompanyViewSet

router = DefaultRouter()

router.register('companies', CompanyViewSet, basename='companies')

urlpatterns = router.urls
