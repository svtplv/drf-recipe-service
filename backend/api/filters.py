from django.db.models import Value
from django_filters import rest_framework as filters

from users.models import User
from recipes.models import Tag


class RecipeFilter(filters.FilterSet):
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )
    author = filters.ModelChoiceFilter(queryset=User.objects.all())

    def filter_is_favorited(self, queryset, name, value):
        if self.request.user.is_authenticated and value:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if self.request.user.is_authenticated and value:
            return queryset.filter(carts__user=self.request.user)
        return queryset


class IngredientFilter(filters.FilterSet):
    name = filters.CharFilter(method='filter_name')

    def filter_name(self, queryset, name, value):
        if value:
            startswith_queryset = queryset.filter(
                name__istartswith=value
            ).annotate(custom_order=Value(1))
            contains_queryset = queryset.filter(
                name__icontains=value
            ).exclude(name__istartswith=value).annotate(custom_order=Value(2))
            return startswith_queryset.union(contains_queryset).order_by(
                'custom_order'
            )
        return queryset
