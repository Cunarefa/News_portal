from django.core.validators import URLValidator
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_bulk import BulkSerializerMixin, BulkListSerializer

from portal_app.models import User, Post, Company


class UserSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    email = serializers.CharField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'first_name', 'last_name', 'phone_number', 'user_type', 'company')

    def create(self, data):
        if data['user_type'] == 'Admin':
            data['is_staff'] = True
        user = User(**data)
        user.set_password(data['password'])
        user.save()
        return user


class UserPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name')


class CompanySerializer(serializers.ModelSerializer):
    url = serializers.URLField(validators=[URLValidator])

    class Meta:
        model = Company
        exclude = ('logo',)


class PostNestedUserSerializer(serializers.ModelSerializer):
    author = UserPostSerializer(read_only=True)

    class Meta:
        model = Post
        fields = '__all__'


class PostSerializer(BulkSerializerMixin, serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Post
        fields = '__all__'
        # list_serializer_class = BulkListSerializer


class PostBulkUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'
        # list_serializer_class = BulkListSerializer
        # update_lookup_field = 'id'


class UserNestedPostsSerializer(serializers.ModelSerializer):
    posts = PostSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ('id', 'posts', 'first_name', 'last_name', 'email')


class SelectionCompanySerializer(serializers.ModelSerializer):
    users = UserNestedPostsSerializer(many=True, read_only=True)

    class Meta:
        model = Company
        fields = ('id', 'name', 'address', 'url', 'users')








