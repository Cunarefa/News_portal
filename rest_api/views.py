from django.contrib.auth.models import update_last_login
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken

from portal_app.models import User, Post, Company
from rest_api.permissions import IsUserOrIsAdminOrReadSelfOnly, CompanyPermissions, PostPermissions
from rest_api.serializers import UserSerializer, PostNestedUserSerializer, CompanySerializer, \
    SelectionCompanySerializer, PostSerializer, PostBulkUpdateSerializer


class LoginView(APIView):
    def post(self, request):
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


class UserViewset(viewsets.ModelViewSet):
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
        return Response(serializer.data)

    def delete(self, request, *args, **kwargs):
        user = self.get_object()
        user.is_active = False
        user.save()
        return Response('User deleted', status.HTTP_200_OK)


class CompanyViewSet(viewsets.ModelViewSet):
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
                serializer = SelectionCompanySerializer(self.queryset, many=True)
                return Response(serializer.data)
            else:
                queryset = self.get_queryset()

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save()


class PostViewSet(viewsets.ModelViewSet):
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
                queryset = queryset.filter(text=text)
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
                return Response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class PostBulkUpdate(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostBulkUpdateSerializer
    permission_classes = [PostPermissions]
    authentication_classes = [JWTAuthentication]

    def update(self, request, *args, **kwargs):
        self.get_object()
        instances = [item for item in request.data]
        for item in request.data:
            post = get_object_or_404(Post, id=item["id"])
            serializer = self.get_serializer(post, data=item)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            instances.append(serializer.data)
        return Response(instances, status.HTTP_200_OK)

