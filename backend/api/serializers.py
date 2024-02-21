from djoser.serializers import UserSerializer
from rest_framework.serializers import SerializerMethodField, ModelSerializer
from users.models import User, Follow
from recipes.models import Tag


class CustomUserSerialiser(UserSerializer):
    is_subscribed = SerializerMethodField()

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


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')
