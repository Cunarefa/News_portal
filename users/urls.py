from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import LoginView, UserViewset, ActivateAccount, PasswordResetView, ConfirmResetPassword

router = DefaultRouter()

router.register('users', UserViewset, basename='users')

urlpatterns = [
    path('login', LoginView.as_view(), name='login'),
    path('resetpassword', PasswordResetView.as_view(), name='reset_password'),
    path('resetpassword/<uidb64>/<password>/', ConfirmResetPassword.as_view(), name='confirm_pass'),
    path('activate/<uidb64>/', ActivateAccount.as_view(), name='activate')
]

urlpatterns += router.urls
