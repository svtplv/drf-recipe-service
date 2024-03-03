from django.contrib import admin

from .forms import TagForm
from .models import Cart, Favorite, Ingredient, Quantity, Recipe, Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    form = TagForm
    list_display = ('name', 'color', 'slug',)
    search_fields = ('name', 'color')
    search_help_text = 'Поиск по названию тега или его слагу.'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    list_filter = ('measurement_unit',)
    search_fields = ('name',)
    search_help_text = 'Поиск по названию ингредиента.'


class QuantityInline(admin.TabularInline):
    autocomplete_fields = ('ingredient',)
    model = Quantity
    extra = 4


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    autocomplete_fields = ('author',)
    inlines = (QuantityInline,)
    list_display = ('name', 'author')
    search_fields = ('name', 'author')
    search_help_text = 'Поиск по названию или автору рецепта.'
    list_filter = ('tags',)

    def change_view(self, request, object_id, extra_context=None):
        self.readonly_fields = ['favorites_count']
        return super().change_view(request, object_id)

    def add_view(self, request, extra_context=None):
        self.readonly_fields = []
        return super().add_view(request)

    def favorites_count(self, obj):
        return obj.favorites.count()

    favorites_count.short_description = 'Количество добавлений в избранное'


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'user')
    autocomplete_fields = ('recipe', 'user')
    search_fields = ('user__username',)
    search_help_text = 'Поиск по пользователю.'


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'user')
    autocomplete_fields = ('recipe', 'user')
    search_fields = ('user__username',)
    search_help_text = 'Поиск по пользователю.'
