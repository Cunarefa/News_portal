from django.contrib.auth.models import update_last_login
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views.generic.base import View
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken

from newsPortal import settings
from portal_app.models import User, Post, Company
from rest_api.permissions import IsUserOrIsAdminOrReadSelfOnly, CompanyPermissions, PostPermissions
from rest_api.serializers import UserSerializer, PostNestedUserSerializer, CompanySerializer, \
    SelectionCompanySerializer, PostSerializer, PostBulkUpdateSerializer, LoginSerializer, PasswordResetSerializer
from .tasks import send_email_task


class LoginView(APIView):

    def get(self, request):
        content = {
            'user': str(request.user),
            'auth': str(request.auth),
        }
        return Response(content, status.HTTP_200_OK)

    @swagger_auto_schema(request_body=LoginSerializer)
    def post(self, request, *args, **kwargs):
        email = request.data['email']
        password = request.data['password']
        user = User.objects.filter(email=email).first()

        if not user or not user.is_active:
            raise AuthenticationFailed('User not found!')

        if not user.check_password(password):
            raise AuthenticationFailed('The password is incorrect!')

        token = RefreshToken.for_user(user)
        update_last_login(None, user)

        return Response({'id': user.id, 'user': user.email, 'access': str(token.access_token), 'refresh': str(token)})


class PasswordResetView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return redirect('login')
        # return Response(serializer.data, status.HTTP_205_RESET_CONTENT)


class ActivateAccount(View):
    def get(self, request, uidb64, *args, **kwargs):
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None:
            user.is_active = True
            user.save()
            return redirect('login')
        else:
            return HttpResponse('Activation link is invalid!')


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
        self.create_email_content(request, serializer)
        return Response(serializer.data, status.HTTP_201_CREATED)

    def create_email_content(self, request, serializer):
        user = User.objects.get(id=serializer.data['id'])
        current_site = get_current_site(request)
        subject = 'Activate your account.'
        message = render_to_string('acc_activate_email.html', {
            'user': user,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        })
        from_email = settings.EMAIL_HOST_USER
        recipient_list = serializer.data['email']
        send_email_task.delay(subject, message, from_email, recipient_list)

    @action(methods=['patch'], detail=True, url_path='password-reset', url_name='password_reset')
    def password_reset(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status.HTTP_205_RESET_CONTENT)
        # return redirect('login')


class CompanyViewSet(ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [CompanyPermissions]

    def list(self, request, *args, **kwargs):
        if not request.user.is_staff:
            queryset = Company.objects.filter(pk=request.user.company.id)
        else:
            selection = self.request.query_params.get('selection')
            if selection:
                queryset = Company.objects.prefetch_related('users', 'users__posts')
                serializer = SelectionCompanySerializer(queryset, many=True)
                return Response(serializer.data, status.HTTP_200_OK)
            else:
                queryset = self.get_queryset()

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status.HTTP_200_OK)

    def perform_create(self, serializer):
        serializer.save()


class PostViewSet(ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostNestedUserSerializer
    permission_classes = [PostPermissions]
    authentication_classes = [JWTAuthentication]

    def list(self, request, *args, **kwargs):
        title = self.request.query_params.get('title')
        text = self.request.query_params.get('text')
        company = self.request.query_params.get('company')
        topic = self.request.query_params.get('topic')

        if request.user.is_staff:
            queryset = self.get_queryset()
            if title:
                queryset = queryset.filter(title=title)
            if text:
                queryset = queryset.filter(text__contains=text)
            if company:
                queryset = queryset.filter(company=company)
            if topic:
                queryset = queryset.filter(topic=topic)
        else:
            if company:
                company = request.user.company
                queryset = Post.objects.filter(author__company=company.id).all()
            else:
                queryset = Post.objects.filter(author=request.user.id)
                serializer = PostSerializer(queryset, many=True)
                return Response(serializer.data, status.HTTP_200_OK)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status.HTTP_200_OK)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def destroy(self, request, *args, **kwargs):
        self.get_object()
        try:
            post = Post.objects.get(id=kwargs["pk"])
            post.is_deleted = True
            post.save()
            return Response(status.HTTP_204_NO_CONTENT)
        except ValueError:
            return Response({'status': 'No post with such id.'}, status.HTTP_404_NOT_FOUND)


class PostBulkUpdate(ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostBulkUpdateSerializer
    authentication_classes = [JWTAuthentication]

    def update(self, request, *args, **kwargs):
        queryset = Post.objects.filter(id__in=[data['id'] for data in request.data])
        serializer = self.get_serializer(queryset, data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    # def bulk_update(self, request, *args, **kwargs):
    #     queryset = Post.objects.filter(id__in=[data['id'] for data in request.data])
    #     serializer = self.get_serializer(queryset, data=request.data, many=True)
    #     serializer.is_valid(raise_exception=True)
    #     self.perform_bulk_update(serializer)
    #     return Response(serializer.data, status=status.HTTP_200_OK)

    # instances = []
    # for item in request.data:
    #     post = get_object_or_404(Post, id=item["id"])
    #     if request.user != post.author and not request.user.is_staff:
    #         raise PermissionDenied("You can not modify other users posts.")
    #
    #     serializer = self.get_serializer(instance=post, data=item)
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save()
    #     instances.append(serializer.data)
    # return Response(instances, status.HTTP_200_OK)

# class PostBulkUpdate(BulkModelViewSet):
#     queryset = Post.objects.all()
#     serializer_class = PostBulkUpdateSerializer
#     authentication_classes = [JWTAuthentication]
#
#     def bulk_update(self, request, *args, **kwargs):
#         instances = Post.objects.filter(id__in=[data['id'] for data in request.data])
#         if request.user != any(instances) and not request.user.is_staff:
#             raise PermissionDenied("You can not modify other users posts.")
#         serializer = self.get_serializer(instance=instances, many=True)
#         serializer.is_valid(raise_exception=True)
#         # serializer.bulk_update()
#         # serializer.save()
#         return Response(serializer.data)
