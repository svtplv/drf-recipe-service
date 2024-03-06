from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.serializers import SetPasswordSerializer, UserCreateSerializer

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response

from foodgram import constants
from recipes.models import Cart, Favorite, Ingredient, Quantity, Recipe, Tag
from users.models import Follow, User
from .filters import IngredientFilter, RecipeFilter
from .mixins import CreateListRetrieveMixin
from .permissions import IsAuthorStaffOrReadOnly
from .serializers import (CartSerializer, FavoriteSerializer, FollowSerializer,
                          IngredientSerializer, RecipeReadSerializer,
                          RecipeWriteSerializer, TagSerializer, UserSerialiser)


class UserViewSet(CreateListRetrieveMixin):
    queryset = User.objects.all()
    serializer_class = UserSerialiser

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerialiser

    @action(
        detail=False,
        methods=('post',),
        permission_classes=(IsAuthenticated,),
    )
    def set_password(self, request):
        user = self.request.user
        serializer = SetPasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        new_password = serializer.validated_data.get('new_password')
        user.set_password(new_password)
        user.save()
        return Response('Пароль успешно изменен', status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthenticated,),
    )
    def me(self, request):
        user = request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data, status.HTTP_200_OK)

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthenticated,),
    )
    def subscriptions(self, request):
        user = request.user
        subscriptions = user.follower.all()
        pages = self.paginate_queryset(subscriptions)
        serializer = FollowSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=('post',),
        permission_classes=(IsAuthenticated,),
    )
    def subscribe(self, request, pk=None):
        get_object_or_404(User, pk=pk)
        data = {'user': request.user.id, 'author': pk}
        serializer = FollowSerializer(
            data=data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data,
            status.HTTP_201_CREATED
        )

    @subscribe.mapping.delete
    def subscribe_delete(self, request, pk=None):
        author = get_object_or_404(User, pk=pk)
        subscription, _ = Follow.objects.filter(
            user=request.user,
            author=author
        ).delete()
        if not subscription:
            return Response(
                {'errors': 'Вы не подписаны на этого пользователя'},
                status.HTTP_400_BAD_REQUEST
            )
        return Response(
            'Успешная отписка',
            status.HTTP_204_NO_CONTENT
        )


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    http_method_names = constants.ALLOWED_METHODS
    permission_classes = (IsAuthorStaffOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeWriteSerializer

    @staticmethod
    def post_common_logic(request, model_serializer, pk):
        """Функция для общей POST логики избранного и списка покупок."""
        data = {'user': request.user.id, 'recipe': pk}
        serializer = model_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data,
            status.HTTP_201_CREATED
        )

    @staticmethod
    def delete_common_logic(user, model, pk):
        """Функция для общей DELETE логики избранного и списка покупок."""
        recipe = get_object_or_404(Recipe, pk=pk)
        obj, _ = model.objects.filter(user=user, recipe=recipe).delete()
        if not obj:
            return Response(
                {'errors': 'Вы не добавляли этот рецепт'},
                status.HTTP_400_BAD_REQUEST
            )
        return Response(
            'Рецепт успешно удален из списка',
            status.HTTP_204_NO_CONTENT
        )

    @action(
        detail=True,
        methods=('post',),
        permission_classes=(IsAuthenticated,),
    )
    def favorite(self, request, pk=None):
        return self.post_common_logic(request, FavoriteSerializer, pk)

    @favorite.mapping.delete
    def favorite_delete(self, request, pk=None):
        return self.delete_common_logic(request.user, Favorite, pk)

    @action(
        detail=True,
        methods=('post',),
        permission_classes=(IsAuthenticated,),
    )
    def shopping_cart(self, request, pk=None):
        return self.post_common_logic(request, CartSerializer, pk)

    @shopping_cart.mapping.delete
    def shopping_cart_delete(self, request, pk=None):
        return self.delete_common_logic(request.user, Cart, pk)

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthenticated,),
    )
    def download_shopping_cart(self, request):
        user = request.user
        ingredients = Quantity.objects.filter(recipe__carts__user=user)
        annotated_ingredients = ingredients.values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(total=Sum('amount'))
        shopping_list = ''
        for ingredient in annotated_ingredients:
            name = ingredient['ingredient__name']
            unit = ingredient['ingredient__measurement_unit']
            total = ingredient['total']
            shopping_list += f'{name}\t{total} {unit}\n'
        response = HttpResponse(
            shopping_list,
            content_type='text/plain; charset=UTF-8'
        )
        response['Content-Disposition'] = ('attachment; filename=list.txt')
        return response
