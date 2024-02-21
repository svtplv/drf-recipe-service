import json

from django.core.management.base import BaseCommand

from recipes.models import Ingredient, Tag


class Command(BaseCommand):
    help = 'Импорт данных из json файла в базу данных'

    def import_data(self, model, file_path):
        """Функция загрузки json-файла и сохрания в базу данных."""
        with open(f'recipes/data/{file_path}', encoding='utf-8') as json_file:
            data = json.load(json_file)
            objects = [model(**object_data) for object_data in data]
            model.objects.bulk_create(objects)

    def handle(self, *args, **options):
        MODEL_PATH = {
            Ingredient: 'ingredients.json',
            Tag: 'tags.json',
        }

        for model, file_path in MODEL_PATH.items():
            self.import_data(model, file_path)
            self.stdout.write(self.style.SUCCESS(
                f'Данные из {file_path} успешно загружены'))
