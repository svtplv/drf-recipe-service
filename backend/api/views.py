from djoser.serializers import UserCreateSerializer, SetPasswordSerializer
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_204_NO_CONTENT
from rest_framework import viewsets

from users.models import User
from recipes.models import Tag, Ingredient, Recipe
from .mixins import CreateListRetrieveMixin
from .serializers import (
    CustomUserSerialiser,
    TagSerializer,
    IngredientSerializer,
    RecipeReadSerializer
)


class UserViewSet(CreateListRetrieveMixin):
    queryset = User.objects.all()
    serializer_class = CustomUserSerialiser

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return CustomUserSerialiser

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
        return Response('Пароль успешно изменен', HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthenticated,),
    )
    def me(self, request):
        user = request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data, HTTP_200_OK)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class RecipeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeReadSerializer
