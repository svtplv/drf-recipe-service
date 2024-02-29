import base64

from django.core.files.base import ContentFile
from djoser.serializers import UserSerializer
from rest_framework import serializers
from users.models import User, Follow
from recipes.models import Tag, Ingredient, Quantity, Recipe, Favorite


class CustomUserSerialiser(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return Follow.objects.filter(user=user, author=obj).exists()
        return False

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )


class FollowSerializer(serializers.ModelSerializer):
    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.ReadOnlyField(default=True)
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.ReadOnlyField(source='author.recipes.count')

    class Meta:
        model = Follow
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )

    def get_recipes(self, obj):
        serializer = RecipeSummarySerializer(obj.author.recipes, many=True,)
        return serializer.data

    def validate(self, data):
        user = self.context.get('user')
        author = self.context.get('author')
        if user == author:
            raise serializers.ValidationError(
                {'errors': 'Вы не можете подписаться на себя'}
            )
        if Follow.objects.filter(user=user, author=author).exists():
            raise serializers.ValidationError(
                {'errors': 'Вы уже подписаны на этого пользователя'}
            )
        return data


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class QuantityReadSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit',
    )

    class Meta:
        model = Quantity
        fields = ('id', 'name', 'measurement_unit', 'amount')


class QuantityWriteSerialier(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    amount = serializers.IntegerField(min_value=1)

    class Meta:
        model = Quantity
        fields = ('id', 'amount')


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class RecipeReadSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True,)
    author = UserSerializer
    ingredients = QuantityReadSerializer(
        many=True,
        source='recipe_ingredients'
    )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time'
        )
        # read_only_fields = ('tags', 'ingredients',)


class RecipeSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class RecipeWriteSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    ingredients = QuantityWriteSerialier(many=True,)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
        )

    def create_ingredients(self, ingredient_data, recipe):
        for obj in ingredient_data:
            amount = obj['amount']
            ingredient = Ingredient.objects.get(id=obj['ingredient']['id'])
            Quantity.objects.create(
                ingredient=ingredient,
                recipe=recipe,
                amount=amount
            )

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        self.create_ingredients(ingredients_data, recipe)
        recipe.tags.add(*tags)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients', None)
        tags = validated_data.pop('tags', None)
        if ingredients:
            instance.ingredients.clear()
            self.create_ingredients(ingredients, instance)
        if tags:
            instance.tags.set(tags)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        serializer = RecipeReadSerializer(instance)
        return serializer.data


class FavoriteSerializer(serializers.ModelSerializer):

    id = serializers.ReadOnlyField(source='recipe.id')
    name = serializers.ReadOnlyField(source='recipe.name')
    image = serializers.ImageField(source='recipe.image', read_only=True)
    cooking_time = serializers.ReadOnlyField(source='recipe.cooking_time')

    class Meta:
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )
        model = Favorite

    def validate(self, data):
        user = self.context.get('user')
        recipe_id = self.context.get('pk')
        if not Recipe.objects.filter(id=recipe_id).exists():
            raise serializers.ValidationError(
                {'errors': 'Данного рецепта не существует'}
            )
        if Favorite.objects.filter(user=user, recipe=recipe_id).exists():
            raise serializers.ValidationError(
                {'errors': 'Этот рецепт уже находится в избранном'}
            )
        return data
