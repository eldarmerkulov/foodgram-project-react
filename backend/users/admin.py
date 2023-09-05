from django.contrib.admin import (
    display,
    ModelAdmin as BaseModelAdmin,
    register
)
from django.contrib.auth.admin import (
    UserAdmin as BaseUserAdmin
)

from .models import Subscribe, User


@register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        'pk',
        'username',
        'first_name',
        'last_name',
        'email',
        'count_recipes',
        'count_followers'
    )
    search_fields = ('username',)
    list_filter = ('username', 'email')
    empty_value_display = '-пусто-'

    @display(description='Рецептов')
    def count_recipes(self, user):
        return user.recipes.count()

    @display(description='Подписчиков')
    def count_followers(self, user):
        return user.subscribers.count()


@register(Subscribe)
class SubscribeAdmin(BaseModelAdmin):
    list_display = ('pk', 'author', 'user')
    search_fields = ('user',)
