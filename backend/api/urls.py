from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, TagViewSet, IngredientViewSet


router_v1 = DefaultRouter()
router_v1.register('users', UserViewSet, 'user')
router_v1.register('tags', TagViewSet, 'tag')
router_v1.register('ingredients', IngredientViewSet, 'ingredient')

urlpatterns = [
    path('', include(router_v1.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
