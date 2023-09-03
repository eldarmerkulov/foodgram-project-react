from django.contrib import admin

from .models import Subscribe, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('pk', 'username', 'first_name', 'last_name', 'email', 'role')
    search_fields = ('username',)
    list_filter = ('username', 'email')
    empty_value_display = '-пусто-'
    list_editable = ('role',)


@admin.register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'author', 'user')
    search_fields = ('user',)
