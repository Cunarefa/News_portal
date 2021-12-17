from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.validators import UniqueValidator

from companies.models import Company
from companies.serializers import CompanySerializer
from users.models import User


class AdminRegisterSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    company = CompanySerializer(required=True)
    email = serializers.EmailField(
        required=True,
        max_length=255,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    class Meta:
        model = User
        exclude = ('is_staff', 'user_permissions', 'groups', 'avatar', 'date_joined', 'is_superuser', 'last_login')

    def create(self, validated_data):
        validated_data['user_type'] = 'Admin'
        validated_data['is_staff'] = True
        company_data = validated_data.pop('company')
        user = User(**validated_data)
        user.set_password(validated_data['password'])

        company = Company.objects.create(**company_data)
        user.company = company
        user.save()
        return user


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
        max_length=255,
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


class InviteUserSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    email = serializers.ListField(child=serializers.CharField(max_length=255))

    class Meta:
        model = User
        fields = ("id", "email",)

    def create(self, validated_data):
        users = []
        emails = validated_data.pop("email")
        for email in emails:
            user = User(email=email)
            user.is_active = False
            users.append(user)

        User.objects.bulk_create(users)
        return users


class AcceptInviteSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    email = serializers.CharField(
        required=True,
        max_length=255,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    class Meta:
        model = User
        exclude = ('is_staff', 'user_permissions', 'groups', 'avatar', 'date_joined', 'is_superuser', 'last_login')

    def update(self, instance, validated_data):
        pass










