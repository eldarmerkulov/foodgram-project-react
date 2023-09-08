from django.contrib import admin
from django.utils.safestring import mark_safe

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
    extra = 0
    min_num = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    fields = (
        'name',
        'tags',
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
        'get_ingredients',
        'get_image',
    )
    list_display_links = (
        'name',
        'author',
    )
    search_fields = ('name', 'author', 'tags',)
    list_filter = ('name', 'author', 'tags',)
    inlines = (IngredientInline,)
    empty_value_display = '-пусто-'

    @admin.display(description='Тэги')
    def get_tags(self, recipe):
        return ', '.join([tag.name for tag in recipe.tags.all()])

    @admin.display(description='Ингредиенты')
    def get_ingredients(self, recipe):
        return ', '.join(
            [
                ingredient.name for ingredient in recipe.ingredients.all()
            ]
        )

    @admin.display(description='В избранном')
    def count_favorites(self, recipe):
        return recipe.favorites.count()

    @admin.display(description='Изображение')
    def get_image(self, obj):
        return mark_safe(f'<img src={obj.image.url} width="60" hieght="40"')


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
