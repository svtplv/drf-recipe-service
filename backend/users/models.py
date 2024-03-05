from django.contrib.auth.validators import UnicodeUsernameValidator
from django.contrib.auth.models import AbstractUser
from django.db import models

from foodgram import constants


class User(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name', 'password')
    email = models.EmailField(
        'Почта',
        unique=True,
    )
    username = models.CharField(
        'Имя пользователя',
        max_length=constants.MAX_USERS_NAME,
        unique=True,
        validators=(UnicodeUsernameValidator(),)
    )
    first_name = models.CharField(
        'Имя',
        max_length=constants.MAX_USERS_NAME,
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=constants.MAX_USERS_NAME,
    )
    password = models.CharField(
        'Пароль',
        max_length=constants.MAX_PASSWORD,
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.username


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        related_name="follower"
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name="followers"
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.CheckConstraint(
                name='prevent_self_follow',
                check=~models.Q(user=models.F('author')),
                violation_error_message='Нельзя подписаться на самого себя'
            ),
            models.UniqueConstraint(
                fields=('user', 'author'),
                name="unique_followers",
            )
        ]

    def __str__(self):
        return f'{self.user} подписан на {self.author}'
