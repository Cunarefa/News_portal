from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Post
from posts.permissions import PostPermissions
from .serializers import PostSerializer, PostBulkUpdateSerializer


class PostViewSet(ModelViewSet):
    queryset = Post.objects.all()
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
        return Response(serializer.data, status.HTTP_200_OK)

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
