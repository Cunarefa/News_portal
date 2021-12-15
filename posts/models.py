from django.db import models

from posts.managers import PostManager
from users.models import User


class Post(models.Model):
    title = models.CharField(max_length=500)
    text = models.TextField(max_length=1000, blank=True, null=True)
    TOPIC_TYPES = (
        ('nature', 'Nature'),
        ('sport', 'Sport'),
        ('art', 'Art'),
        ('travel', 'Travel')
    )
    topic = models.CharField(choices=TOPIC_TYPES, max_length=6)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    is_deleted = models.BooleanField(default=False)
    objects = PostManager()
    all_objects = models.Manager()

    def __str__(self):
        return self.title
