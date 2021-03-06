from datetime import datetime

import jwt
from django.contrib.auth.models import update_last_login
from django.core.exceptions import ValidationError, ObjectDoesNotExist

from django.http import JsonResponse
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.views import View
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.generics import CreateAPIView, UpdateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.backends import TokenBackend
from rest_framework_simplejwt.tokens import RefreshToken

import conf
from users.models import User, InviteToken
# from .tasks import create_email_content
from users.permissions import IsUserOrIsAdminOrReadSelfOnly
from users.serializers import LoginSerializer, PasswordResetSerializer, UserSerializer, AdminRegisterSerializer, \
    InviteUserSerializer, AcceptInviteSerializer
from rest_framework.authtoken.models import Token
from newsPortal.settings import SECRET_KEY as secret


class AdminRegistrationView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = AdminRegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        token = RefreshToken.for_user(serializer.instance)
        update_last_login(None, serializer.instance)
        data = {
            'user': serializer.data,
            'access_token': str(token.access_token)
        }
        return Response(data, status.HTTP_201_CREATED)


class InviteUsers(CreateAPIView):
    serializer_class = InviteUserSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsUserOrIsAdminOrReadSelfOnly]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"Invites sent to ": serializer.validated_data}, status.HTTP_201_CREATED)


class AcceptInvite(UpdateAPIView):
    serializer_class = AcceptInviteSerializer
    permission_classes = [AllowAny]

    def get_object(self, **kwargs):
        try:
            token = kwargs['token']
            obj = InviteToken.objects.get(value=token).user
            return obj
        except ValidationError as v:
            print("validation error", v)

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        try:
            user = self.get_object(**kwargs)

            if not request.data.get('email'):
                request.data['email'] = user.email

            serializer = self.get_serializer(user, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            token = InviteToken.objects.get(value=kwargs['token'])
            token.status = False
            token.exp_date = datetime.now()
            token.save()
            return Response(serializer.data, status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response(
                {'message': "InviteToken object does not exist or have expired"}, status.HTTP_404_NOT_FOUND
            )


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

        data = {
            'message': 'Check your email.'
        }
        return Response(data, status=200)


class ConfirmResetPassword(APIView):
    def post(self, request, *args, **kwargs):
        token_data = jwt.decode(kwargs['token'], secret, algorithms=['HS256'])
        uid = token_data['user_id']
        password = token_data['password']

        user = User.objects.get(pk=uid)
        user.password = password
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
            token_data = jwt.decode(kwargs['token'], secret, algorithms=['HS256'])
            uid = token_data['user_id']
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
        return Response(serializer.data, status.HTTP_201_CREATED)
