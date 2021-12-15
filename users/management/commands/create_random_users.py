import random

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.hashers import make_password
from django.core.management import BaseCommand
from faker import Faker

from companies.models import Company
from users.models import User

fake = Faker()


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('total', type=int, help=u'Amount created users')

    def handle(self, *args, **kwargs):
        total = kwargs['total']
        users = []
        companies = Company.objects.all()

        if companies:
            for _ in range(total):
                user = User(email=fake.unique.email(),
                            password=make_password(BaseUserManager().make_random_password()),
                            user_type='Client',
                            first_name=fake.first_name(),
                            last_name=fake.last_name(),
                            phone_number=fake.phone_number(),
                            company=random.choice(companies)
                            )

                users.append(user)

            User.objects.bulk_create(users)
        else:
            return 'There is no company in db.'

