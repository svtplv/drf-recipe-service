from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from users.models import User


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
        return f'{self.name} ({self.measurement_unit})'


class Recipe(models.Model):
    name = models.CharField(
        'Название',
        max_length=settings.MAX_RECIPE_NAME,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='recipes',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='Quantity',
        verbose_name='Ингредиенты',
        related_name='recipes',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
        related_name='recipes'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='media/',
    )
    text = models.TextField('Описание',)
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления',
        validators=(MinValueValidator(settings.MIN_COOKING_TIME),)
    )
    pub_date = models.DateTimeField('Время публикации', auto_now_add=True)

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class Quantity(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
        related_name='recipe_ingredients'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='recipe_ingredients'
    )
    amount = models.PositiveSmallIntegerField(
        'Количество',
        validators=(MinValueValidator(settings.MIN_INGREDIENT_AMOUNT),)
    )

    class Meta:
        verbose_name_plural = 'Ингредиенты рецепта'

    def __str__(self):
        return (
            f'{self.ingredient.name} {self.amount} '
            f'{self.ingredient.measurement_unit}'
        )
