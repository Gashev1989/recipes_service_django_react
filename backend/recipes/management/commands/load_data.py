import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from recipes.models import Ingredient

FILE_ROOT = os.path.join(settings.BASE_DIR, 'data/ingredients.csv')


class Command(BaseCommand):
    help = 'Загрузка ингридиентов из csv файла.'

    def handle(self, *args, **options):
        try:
            with open(FILE_ROOT, 'r', encoding='utf-8') as file:
                data = csv.reader(file)
                for row in data:
                    Ingredient.objects.get_or_create(
                        name=row[0], measurement_unit=row[1])
                self.stdout.write(
                    self.style.SUCCESS('Данные успешно загружены!')
                )
        except FileNotFoundError:
            raise CommandError('Файл ingredients.csv не найден!')
