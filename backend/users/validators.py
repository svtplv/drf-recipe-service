import re

from django.conf import settings
from django.core.exceptions import ValidationError


def validate_username(value):
    if value in settings.FORBIDDEN_WORDS:
        raise ValidationError(f'Имя пользователя не может быть {value}')

    unexpected_symbols = re.sub(r'[\w.@+-]+', '', value)
    if unexpected_symbols:
        raise ValidationError(
            'Имя пользователя не должно содержать следующих символов: '
            f'{unexpected_symbols}'
        )
