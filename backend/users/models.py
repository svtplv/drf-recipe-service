from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

from .validators import validate_username


class User(AbstractUser):
    email = models.EmailField(
        'Почта',
        max_length=settings.MAX_EMAIL,
        unique=True,
    )
    username = models.CharField(
        'Имя пользователя',
        max_length=settings.MAX_USERS_NAME,
        unique=True,
        validators=(validate_username,)
    )
    first_name = models.CharField(
        'Имя',
        max_length=settings.MAX_USERS_NAME,
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=settings.MAX_USERS_NAME,
    )
    password = models.CharField(
        'Пароль',
        max_length=settings.MAX_PASSWORD,
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.username
