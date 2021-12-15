from rest_framework import serializers
from rest_framework.serializers import ListSerializer

from posts.models import Post


class PostSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Post
        fields = '__all__'


class PostListUpdate(ListSerializer):
    def update(self, queryset, validated_data):
        post_mapping = {post.id: post for post in queryset}
        data_mapping = {data.pop('id'): data for data in self.initial_data}

        updated_objects = []

        for obj_id, data in data_mapping.items():
            post = post_mapping.get(obj_id)
            updated_objects.append(self.child.update(post, data))

        return updated_objects


class PostBulkUpdateSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.id')

    class Meta:
        model = Post
        fields = '__all__'
        list_serializer_class = PostListUpdate
