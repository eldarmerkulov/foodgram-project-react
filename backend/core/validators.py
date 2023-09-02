import re

from django.core.exceptions import ValidationError

from .constant import FORBIDDEN_SYMBOLS


def validate_username(value):
    if value.lower() == 'me':
        raise ValidationError(
            f'Нелья присваивать username {value}'
        )
    forbidden_symbol = ''.join(
        set(re.sub(FORBIDDEN_SYMBOLS, '', value))
    )
    if forbidden_symbol:
        raise ValidationError(
            f'Запрещенные символы в имени: {forbidden_symbol}'
        )
    return value