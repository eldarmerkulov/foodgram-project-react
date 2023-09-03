from django.db import models

import sys
from os import path
__path__ = path.dirname(path.abspath(__file__))
__parent__ = path.abspath(path.join(__path__, ".."))
sys.path.append(__parent__)

from users.models import User
from core.constant import (
    BLUE,
    GREEN,
    LENGTH_INGREDIENT_NAME,
    LENGTH_INGREDIENT_UNIT,
    LENGTH_RECIPE_NAME,
    LENGTH_TAG_COLOR,
    LENGTH_TAG_NAME,
    LENGTH_TAG_SLUG,
    PURPLE
)

COLOR_CHOICES = (
        (BLUE, 'Синий'),
        (GREEN, 'Зеленый'),
        (PURPLE, 'Фиолетовый'),
)


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Наименование',
        max_length=LENGTH_TAG_NAME,
        unique=True,
    )
    color = models.CharField(
        verbose_name='Цвет',
        max_length=LENGTH_TAG_COLOR,
        choices=COLOR_CHOICES,
    )
    slug = models.SlugField(
        verbose_name='Slug',
        max_length=LENGTH_TAG_SLUG,
        unique=True,
        )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Наименование',
        max_length=LENGTH_INGREDIENT_NAME,
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=LENGTH_INGREDIENT_UNIT,
    )

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'
        ordering = ('name',)
        constraints = (
            models.UniqueConstraint(
                fields=(
                    'name',
                    'measurement_unit',
                ),
                name='ingredient is already exists.',
            ),
        )

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Recipe(models.Model):
    tags = models.ManyToManyField(
        verbose_name='Тэг',
        to=Tag,
        related_name='recipes',
    )
    author = models.ForeignKey(
        verbose_name='Пользователь',
        to=User,
        related_name='recipes',
        on_delete=models.CASCADE,
    )
    ingredients = models.ManyToManyField(
        verbose_name='Ингридиенты',
        to=Ingredient,
        related_name='recipes',
        through='recipes.IngredientAmount',
    )
    name = models.CharField(
        verbose_name='Наименование',
        max_length=LENGTH_RECIPE_NAME,
    )
    image = models.ImageField(
        verbose_name='Изображение',
        upload_to='recipes/images/',
    )
    text = models.TextField(
        verbose_name='Описание',
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        default=1,
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
        editable=False,
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name


class Favorite(models.Model):
    user = models.ForeignKey(
        verbose_name='Пользователь',
        to=User,
        related_name='favorites',
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        verbose_name='Избранные рецепты',
        to=Recipe,
        related_name='in_favorites',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = (
            models.UniqueConstraint(
                fields=(
                    'user',
                    'recipe',
                ),
                name='recipe is already in favorite.',
            ),
        )

    def __str__(self) -> str:
        return f'{self.user} любит {self.recipe}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        verbose_name='Пользователь',
        to=User,
        related_name='shoppingcarts',
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        verbose_name='Избранные рецепты',
        to=Recipe,
        related_name='in_shoppingcarts',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = (
            models.UniqueConstraint(
                fields=(
                    'user',
                    'recipe',
                ),
                name='recipe is already in shopping cart.',
            ),
        )


class IngredientAmount(models.Model):
    recipe = models.ForeignKey(
        verbose_name='Рецепт',
        to=Recipe,
        related_name='ingredient',
        on_delete=models.CASCADE,
    )
    ingredient = models.ForeignKey(
        verbose_name='Ингридиент',
        to=Ingredient,
        related_name='recipe',
        on_delete=models.CASCADE,
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        default=0,
    )

    class Meta:
        verbose_name = 'Ингридиенты'
        verbose_name_plural = 'Все ингридиенты'
        ordering = ('recipe',)
        constraints = (
            models.UniqueConstraint(
                fields=(
                    'recipe',
                    'ingredient',
                ),
                name='ingredient already added.',
            ),
        )

    def __str__(self) -> str:
        return f'{self.ingredient} в количестве {self.amount}.'
