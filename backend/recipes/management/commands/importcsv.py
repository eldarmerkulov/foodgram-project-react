import csv

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredient, Tag

MODELS = {
    Ingredient: 'ingredients.csv',
    Tag: 'tags.csv',
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
                    count = sum(
                        [
                            item for _, item in [
                                model.objects.get_or_create(
                                    **row
                                ) for row in data
                            ]
                        ]
                    )

                self.stdout.write(
                    self.style.SUCCESS(
                        'Successfully import csv'
                        ' files into database: '
                        f'{model.__name__} - {count} row added.'
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
