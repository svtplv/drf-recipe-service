from django.contrib import admin

from .forms import TagForm
from .models import Tag, Ingredient


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    form = TagForm
    list_display = ('name', 'color', 'slug',)
    search_fields = ('name', 'color')
    search_help_text = 'Поиск по названию тега или его слагу.'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    search_fields = ('name',)
    search_help_text = 'Поиск по названию ингредиента.'
