from django.contrib.auth.models import update_last_login
from django.contrib.sites.shortcuts import get_current_site
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.utils.encoding import force_text, force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views import View
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken

import conf
from newsPortal import settings
from users.models import User
from .tasks import send_email_task
from users.permissions import IsUserOrIsAdminOrReadSelfOnly
from users.serializers import LoginSerializer, PasswordResetSerializer, UserSerializer


class LoginView(APIView):

    @swagger_auto_schema(request_body=LoginSerializer)
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = RefreshToken.for_user(serializer.validated_data)
        update_last_login(None, serializer.validated_data)
        data = {
            'user': serializer.data,
            'access_token': str(token.access_token)
        }
        return Response(data, status.HTTP_200_OK)


class PasswordResetView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        subject = conf.RESET_SUBJECT
        template = 'reset_password.html'
        password = serializer.data['password']
        create_email_content(request, serializer, subject, template, password)
        data = {
            'message': 'Check your email.'
        }
        return JsonResponse(data, status=200)


class ConfirmResetPassword(APIView):
    def post(self, request, *args, **kwargs):
        try:
            uid = force_text(urlsafe_base64_decode(kwargs['uidb64']))
            password = force_text(urlsafe_base64_decode(kwargs['password']))
            user = User.objects.get(pk=uid)
            user.password = password
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        serializer = LoginSerializer(instance=user)
        user.save()
        token = RefreshToken.for_user(user)
        update_last_login(None, user)
        data = {
            'user': serializer.data,
            'access_token': str(token.access_token)
        }
        return JsonResponse(data, status=200)


class ActivateAccount(View):
    def get(self, request, *args, **kwargs):
        try:
            uid = force_text(urlsafe_base64_decode(kwargs.get('uidb64')))
            user = User.objects.get(pk=uid)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        serializer = UserSerializer(instance=user)
        user.is_active = True
        user.save()
        token = RefreshToken.for_user(user)
        update_last_login(None, user)
        data = {
            'user': serializer.data,
            'access_token': str(token.access_token)
        }
        return JsonResponse(data, status=200)


class UserViewset(ModelViewSet):
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsUserOrIsAdminOrReadSelfOnly]

    def list(self, request, *args, **kwargs):
        if not request.user.is_staff:
            queryset = User.objects.filter(pk=request.user.id)
        else:
            queryset = User.objects.all()

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        user = User.objects.get(id=kwargs["pk"])
        # user = self.get_object()
        # user.is_active = False
        user.delete()
        return Response(status.HTTP_204_NO_CONTENT)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        subject = conf.ACTIVATE_SUBJECT
        template = 'acc_activate_email.html'
        create_email_content(request, serializer, subject, template)
        return Response(serializer.data, status.HTTP_201_CREATED)


def create_email_content(request, serializer, subject, template, password=None):
    current_site = get_current_site(request)
    message = render_to_string(template, {
        'user': serializer,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(serializer.data['id'])),
        'password': urlsafe_base64_encode(force_bytes(password)),
    })
    from_email = settings.EMAIL_HOST_USER
    recipient_list = serializer.data['email']
    send_email_task.delay(subject, message, from_email, recipient_list)
