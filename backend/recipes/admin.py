from django.contrib import admin
from .models import (
    Ingredient,
    IngredientAmount,
    Favorite,
    Recipe,
    ShoppingCart,
    Tag
)


class IngredientInline(admin.TabularInline):
    model = IngredientAmount
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    fields = (
        'name',
        'tag',
        'author',
        'text',
        'image',
        'cooking_time',
    )
    list_display = (
        'pk',
        'name',
        'get_tags',
        'author',
        'count_favorites',
    )
    search_fields = ('name', 'author', 'tag',)
    list_filter = ('name', 'author', 'tag',)
    inlines = (IngredientInline,)
    empty_value_display = '-пусто-'

    def get_tags(self, recipe):
        return "\n".join([tag.name for tag in recipe.tag.all()])

    get_tags.short_description = 'Тэги'

    def count_favorites(self, recipe):
        return recipe.in_favorites.count()

    count_favorites.short_description = 'В избранном'


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe',)
    search_fields = ('user', 'recipe',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'color',)
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe',)
    # search_fields = ('username',)
    # empty_value_display = '-пусто-'
    # list_filter = ('role',)
    # list_editable = ('role',)
