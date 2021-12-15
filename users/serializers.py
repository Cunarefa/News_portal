from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.validators import UniqueValidator

from posts.serializers import PostSerializer
from users.models import User


class LoginSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    email = serializers.EmailField(max_length=255)
    password = serializers.CharField(max_length=128, write_only=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'company')

    def validate(self, data):
        user = User.objects.filter(email=data.get('email')).first()

        if not user or not user.is_active:
            raise AuthenticationFailed('User not found!')

        if not user.check_password(data['password']):
            raise AuthenticationFailed('The password is incorrect!')

        return user


class PasswordResetSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255)
    password = serializers.CharField(max_length=128, required=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'password')

    def validate(self, data):
        user = User.objects.filter(email=data.get('email')).first()
        password = data['password']

        if not user or not user.is_active:
            raise AuthenticationFailed('User not found!')

        user.set_password(password)
        return user


class UserSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    email = serializers.CharField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    user_type = serializers.ChoiceField(choices=User.ROLES, default='Client')
    company = serializers.IntegerField(required=True, source='company_id')

    class Meta:
        model = User
        exclude = ('is_staff', 'user_permissions', 'groups', 'avatar', 'date_joined', 'is_superuser', 'last_login')

    def create(self, validated_data):
        if validated_data['user_type'] == 'Admin':
            validated_data['is_staff'] = True
        user = User(**validated_data)
        user.set_password(validated_data['password'])
        user.is_active = False
        user.save()
        return user


class UserNestedPostsSerializer(serializers.ModelSerializer):
    posts = PostSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ('id', 'posts', 'first_name', 'last_name', 'email')

