from django.contrib.auth.models import AbstractUser
from django.db import models

import sys
from os import path
__path__ = path.dirname(path.abspath(__file__))
__parent__ = path.abspath(path.join(__path__, ".."))
sys.path.append(__parent__)
from core.constant import (
    ADMIN,
    LENGTH_EMAIL,
    LENGTH_USER_NAME,
    LENGTH_USER_PASS,
    MAX_SCORE,
    MIN_SCORE,
    USER
)
from core.validators import validate_username


ROLE_CHOICES = (
    (USER, 'Пользователь'),
    (ADMIN, 'Администратор'),
)


class User(AbstractUser):
    username = models.CharField(
        verbose_name='Имя пользователя',
        max_length=LENGTH_USER_NAME,
        validators=[validate_username],
        unique=True
    )
    email = models.EmailField(
        verbose_name='Почта',
        unique=True,
        max_length=LENGTH_EMAIL,
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=LENGTH_USER_NAME,
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=LENGTH_USER_NAME,
    )
    role = models.CharField(
        'Полномочия',
        max_length=max(len(role_name) for role_name, _ in ROLE_CHOICES),
        choices=ROLE_CHOICES,
        default=USER
    )
    password = models.CharField(
        verbose_name='Пароль',
        max_length=LENGTH_USER_PASS,
    )

    class Meta(AbstractUser.Meta):
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    @property
    def is_admin(self):
        return (self.role == ADMIN
                or self.is_superuser
                or self.is_staff)

    def __str__(self):
        return f'{self.last_name} {self.first_name}'


class Subscribe(models.Model):
    user = models.ForeignKey(
        verbose_name='Подписчик',
        to=User,
        related_name='authors',
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        verbose_name='Автор',
        to=User,
        related_name='subscribers',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = (
            models.UniqueConstraint(
                fields=('author', 'user'),
                name='unique_members',
            ),
            models.CheckConstraint(
                check=~models.Q(author=models.F('user')),
                name='prevent_self_follow'
            ),
        )

    def __str__(self) -> str:
        return f'{self.user} подписан на {self.author}'
