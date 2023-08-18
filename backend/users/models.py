from django.contrib.auth.models import AbstractUser
from django.db import models

from ..recipes.constant import (ADMIN, LENGTH_EMAIL, LENGTH_NAME,
                                LENGTH_NAME_USER, LENGTH_SLUG, MAX_SCORE,
                                MIN_SCORE, USER)

ROLE_CHOICES = (
    (USER, 'Пользователь'),
    (ADMIN, 'Администратор'),
)


class User(AbstractUser):
    username = models.CharField(
        verbose_name='Имя пользователя',
        max_length=LENGTH_NAME_USER,
        # validators=[validate_username],
        unique=True
    )
    email = models.EmailField(
        verbose_name='Почта',
        unique=True,
        max_length=LENGTH_EMAIL,
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=LENGTH_NAME_USER,
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=LENGTH_NAME_USER,
    )
    role = models.CharField(
        'Полномочия',
        max_length=max(len(role_name) for role_name, _ in ROLE_CHOICES),
        choices=ROLE_CHOICES,
        default=USER
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
        related_name='users',
        on_delete=models.CASCADE,
        required=True,
    )
    author = models.ForeignKey(
        verbose_name='Автор',
        to=User,
        related_name='users',
        on_delete=models.CASCADE,
        required=True,
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
