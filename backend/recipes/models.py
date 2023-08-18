from django.db import models

from users import User
from .constant import (LENGTH_EMAIL, LENGTH_NAME,
                       LENGTH_NAME_USER, LENGTH_SLUG,
                       MAX_SCORE, MIN_SCORE)


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Наименование',
        max_length=LENGTH_NAME, #200
        unique=True,
    )
    color = models.CharField(
        verbose_name='Цвет',
        max_length=LENGTH_NAME, #7
        unique=True,
        # Добавить проверку на регулярку ^[-a-zA-Z0-9_]+$
    )
    slug = models.SlugField(
        verbose_name='Slug',
        max_length=LENGTH_SLUG, #200
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
        max_length=LENGTH_NAME, #200
        required=True,
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=LENGTH_NAME, #200
        required=True,
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
    tag = models.ManyToManyField(
        verbose_name='Тэг',
        to=Tag,
        related_name='recipes',
    )
    author = models.ForeignKey(
        verbose_name='Пользователь',
        to=User,
        related_name='recipes',
        on_delete=models.CASCADE,
        required=True,
    )
    ingredients = models.ManyToManyField(
        verbose_name='Ингридиенты',
        to=Ingredient,
        related_name='recipes',
        through='recipes.IngredientAmount',
    )
    name = models.CharField(
        verbose_name='Наименование',
        max_length=LENGTH_NAME, #200
        required=True,
    )
    image = models.ImageField(
        verbose_name='Изображение',
        upload_to='recipes/',
        required=True,
    )
    text = models.TextField(
        verbose_name='Описание',
        required=True,
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        default=0,
        # валидатор времени
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
        # validators=(
        #     MinValueValidator(
        #         Limits.MIN_AMOUNT_INGREDIENTS,
        #         'Нужно хоть какое-то количество.',
        #     ),
        #     MaxValueValidator(
        #         Limits.MAX_AMOUNT_INGREDIENTS,
        #         'Слишком много!',
        #     ),
        # ),
    )

    class Meta:
        verbose_name = 'Ингридиенты'
        verbose_name_plural = 'Все ингридиенты'
        ordering = ('recipe',)
        constraints = (
            models.UniqueConstraint(
                fields=(
                    'recipe',
                    'ingredients',
                ),
                name='ingredient already added.',
            ),
        )

    def __str__(self) -> str:
        return f'{self.ingredient} в количестве {self.amount}.'
