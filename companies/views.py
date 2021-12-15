from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication

from companies.models import Company
from companies.permissions import CompanyPermissions
from companies.serializers import CompanySerializer, SelectionCompanySerializer


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
