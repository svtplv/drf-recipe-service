from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, TagViewSet


router_v1 = DefaultRouter()
router_v1.register('users', UserViewSet, 'user')
router_v1.register('tags', TagViewSet, 'tag')

urlpatterns = [
    path('', include(router_v1.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
