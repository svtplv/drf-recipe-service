from django.conf import settings
from django.db import models


class Tag(models.Model):
    name = models.CharField(
        'Название',
        max_length=settings.MAX_TAG_NAME,
        unique=True,
    )
    color = models.CharField(
        'Цвет в HEX',
        max_length=settings.HEX_LEN,
        null=True
    )
    slug = models.SlugField(
        'Уникальный слаг',
        max_length=settings.MAX_TAG_SLUG,
        unique=True,
        null=True
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        'Ингредиент',
        max_length=settings.MAX_INGREDIENT_NAME,
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=settings.MAX_INGREDIENT_UNIT,
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name
