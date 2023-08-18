import csv

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredient

MODELS = {
    Ingredient: 'ingredients.csv',
}


class Command(BaseCommand):
    help = 'Import csv files into database'

    def handle(self, *args, **options):
        for model, csv_name in MODELS.items():
            try:
                with open(
                        f'{settings.BASE_DIR}/data/{csv_name}',
                        'r',
                        encoding='utf-8'
                ) as csv_file:
                    data = csv.DictReader(csv_file)
                    model.objects.bulk_create(
                        [model(**row) for row in data],
                        ignore_conflicts=True,
                    )
                self.stdout.write(
                    self.style.SUCCESS(
                        'Successfully import csv'
                        ' files into database: {}'.format(
                            model.__name__,
                        )
                    )
                )
            except FileNotFoundError:
                self.stdout.write(
                    self.style.ERROR('File {} not found'.format(csv_name))
                )
            except Exception as error:
                self.stdout.write(
                    self.style.ERROR(
                        'Error while working with file: {}. Error: {}'.format(
                            csv_name, error
                        )
                    )
                )
