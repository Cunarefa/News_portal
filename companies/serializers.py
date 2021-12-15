from django.core.validators import URLValidator
from rest_framework import serializers
from companies.models import Company
from users.serializers import UserNestedPostsSerializer


class CompanySerializer(serializers.ModelSerializer):
    url = serializers.URLField(validators=[URLValidator])

    class Meta:
        model = Company
        exclude = ('logo',)


class SelectionCompanySerializer(serializers.ModelSerializer):
    users = UserNestedPostsSerializer(many=True, read_only=True)

    class Meta:
        model = Company
        fields = ('id', 'name', 'address', 'url', 'users')








