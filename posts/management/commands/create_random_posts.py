import random

from django.core.management import BaseCommand
from faker import Faker

from companies.models import Company
from posts.models import Post
from users.models import User

fake = Faker()


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('total', type=int, help=u'Amount created posts')

    def handle(self, *args, **kwargs):
        total = kwargs['total']
        posts = []
        users = User.objects.all()

        if users:
            for user in users:
                for _ in range(total):
                    post = Post(title=fake.text(max_nb_chars=20),
                                text=fake.text(max_nb_chars=150),
                                topic=random.choice(['nature', 'sport', 'travel', 'art']),
                                author=user
                                )

                    posts.append(post)

            Post.objects.bulk_create(posts)
        else:
            return 'There is no user in db.'

