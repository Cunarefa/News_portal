from django.urls import path
from rest_framework.routers import DefaultRouter

from users.views import LoginView, UserViewset, ActivateAccount, PasswordResetView, ConfirmResetPassword, \
    AdminRegistrationView, InviteUsers, AcceptInvite

router = DefaultRouter()

router.register('users', UserViewset, basename='users')

urlpatterns = [
    path('register', AdminRegistrationView.as_view(), name='register'),
    path('login', LoginView.as_view(), name='login'),
    path('reset-password', PasswordResetView.as_view(), name='reset_password'),
    path('reset-password/<token>', ConfirmResetPassword.as_view(), name='confirm_pass'),
    path('activate/<uidb64>', ActivateAccount.as_view(), name='activate'),
    path('invite-users', InviteUsers.as_view(), name='invite'),
    path('accept-invite/<token>', AcceptInvite.as_view(), name='accept_invite'),
]

urlpatterns += router.urls
