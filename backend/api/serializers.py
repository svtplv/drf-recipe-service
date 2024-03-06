import base64

from django.core.files.base import ContentFile
from rest_framework import serializers

from recipes.models import Cart, Favorite, Ingredient, Quantity, Recipe, Tag
from users.models import Follow, User


class UserSerialiser(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

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

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        print()
        return bool(
            request and request.user.is_authenticated
            and Follow.objects.filter(user=request.user, author=obj).exists()
        )


class AuthorReadSerializer(UserSerialiser):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.ReadOnlyField(source='recipes.count')

    class Meta(UserSerialiser.Meta):
        fields = UserSerialiser.Meta.fields + ('recipes', 'recipes_count')

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.query_params.get('recipes_limit')
        recipes = obj.recipes.all()
        if limit and limit.isdigit():
            recipes = recipes[:int(limit)]
        serializer = RecipeSummarySerializer(recipes, many=True,)
        return serializer.data


class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = ('user', 'author')

    def validate(self, data):
        if data['user'] == data['author']:
            raise serializers.ValidationError(
                {'errors': 'Вы не можете подписаться на себя'}
            )
        if Follow.objects.filter(**data).exists():
            raise serializers.ValidationError(
                {'errors': 'Вы уже подписаны на этого пользователя'}
            )
        return data

    def to_representation(self, instance):
        serializer = AuthorReadSerializer(
            instance.author,
            context={'request': self.context.get('request')}
        )
        return serializer.data


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
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

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
    author = UserSerialiser()
    ingredients = QuantityReadSerializer(
        many=True,
        source='recipe_ingredients'
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        return bool(
            request and request.user.is_authenticated
            and Favorite.objects.filter(user=request.user, recipe=obj).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        return bool(
            request and request.user.is_authenticated
            and Cart.objects.filter(user=request.user, recipe=obj).exists()
        )


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

    @staticmethod
    def create_ingredients(ingredient_data, recipe):
        objects = [Quantity(
            ingredient=obj['id'],
            amount=obj['amount'],
            recipe=recipe,
        ) for obj in ingredient_data]
        Quantity.objects.bulk_create(objects)

    def create(self, validated_data):
        validated_data['author'] = self.context.get('request').user
        ingredients_data = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        self.create_ingredients(ingredients_data, recipe)
        recipe.tags.add(*tags)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance.ingredients.clear()
        self.create_ingredients(ingredients, instance)
        instance.tags.set(tags)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        serializer = RecipeReadSerializer(
            instance,
            context={'request': self.context.get('request')}
        )
        return serializer.data

    def validate_ingredients(self, value):
        if not value:
            raise serializers.ValidationError(
                'Нужно указать хотя бы один ингредиент'
            )
        ingredient_ids = [obj['id'] for obj in value]
        if len(ingredient_ids) > len(set(ingredient_ids)):
            raise serializers.ValidationError(
                'Ингредиенты не должны повторяться'
            )
        return value

    def validate_tags(self, value):
        if not value:
            raise serializers.ValidationError(
                'Нужно указать хотя бы один тег'
            )
        if len(value) > len(set(value)):
            raise serializers.ValidationError(
                'Теги не должны повторяться'
            )
        return value

    def validate(self, data):
        errors = {
            field: 'Обязательное поле' for field in
            ('ingredients', 'tags') if field not in data
        }
        if errors:
            raise serializers.ValidationError(errors)
        return data


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('user', 'recipe')
        model = Favorite

    def validate(self, data):
        if self.Meta.model.objects.filter(**data).exists():
            raise serializers.ValidationError(
                {'errors': 'Вы уже добавляли этот рецепт'}
            )
        return data

    def to_representation(self, instance):
        serializer = RecipeSummarySerializer(
            instance.recipe,
            context={'request': self.context.get('request')}
        )
        return serializer.data


class CartSerializer(FavoriteSerializer):
    class Meta(FavoriteSerializer.Meta):
        model = Cart
