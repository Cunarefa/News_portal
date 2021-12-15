from django.core.management import BaseCommand
from faker import Faker

from companies.models import Company

fake = Faker()


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('total', type=int, help=u'Amount created posts')

    def handle(self, *args, **kwargs):
        total = kwargs['total']
        companies = []

        for _ in range(total):
            company = Company(name=fake.company(),
                              date_created=fake.date()
                              )
            name = ''.join(char for char in company.name.lower() if char.isalnum())
            company.url = f'https://www.{name}.com'
            companies.append(company)

        Company.objects.bulk_create(companies)