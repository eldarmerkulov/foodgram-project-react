from django.contrib.auth.models import AbstractUser
from django.db import models

from core.constant import LENGTH_EMAIL, LENGTH_USER
from core.validators import validate_username


class User(AbstractUser):
    username = models.CharField(
        verbose_name='Имя пользователя',
        max_length=LENGTH_USER,
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
        max_length=LENGTH_USER,
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=LENGTH_USER,
    )
    password = models.CharField(
        verbose_name='Пароль',
        max_length=LENGTH_USER,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')

    class Meta(AbstractUser.Meta):
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    @property
    def is_admin(self):
        return (self.is_superuser
                or self.is_staff)

    def __str__(self):
        return self.get_full_name()


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
