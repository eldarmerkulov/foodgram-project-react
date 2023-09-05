from colorfield.fields import ColorField
from django.db import models
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
)

from users.models import User
from core.constant import (
    BLUE,
    GREEN,
    LENGTH_NAME,
    LENGTH_TAG_COLOR,
    MAX_SCORE,
    MIN_SCORE,
    PURPLE,
)

COLOR_CHOICES = (
    (BLUE, 'Синий'),
    (GREEN, 'Зеленый'),
    (PURPLE, 'Фиолетовый'),
)


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Наименование',
        max_length=LENGTH_NAME,
        unique=True,
    )
    color = ColorField(
        verbose_name='Цвет',
        max_length=LENGTH_TAG_COLOR,
        samples=COLOR_CHOICES,
    )
    slug = models.SlugField(
        verbose_name='Slug',
        max_length=LENGTH_NAME,
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
        max_length=LENGTH_NAME,
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=LENGTH_NAME,
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
                name='unique_ingredient_measurement_unit',
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
        max_length=LENGTH_NAME,
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
        validators=[
            MaxValueValidator(
                MAX_SCORE,
                f'Время не более {MAX_SCORE}'
            ),
            MinValueValidator(
                MIN_SCORE,
                f'Время не менее {MIN_SCORE}'
            )
        ],
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


class UserRecipeAdddateModel(models.Model):
    user = models.ForeignKey(
        verbose_name='Пользователь',
        to=User,
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        verbose_name='Избранные рецепты',
        to=Recipe,
        on_delete=models.CASCADE,
    )
    add_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
        editable=False,
    )

    class Meta:
        abstract = True
        ordering = ('-add_date',)
        constraints = (
            models.UniqueConstraint(
                fields=(
                    'user',
                    'recipe',
                ),
                name='%(class)s_unique_recipe_user',
            ),
        )


class Favorite(UserRecipeAdddateModel):

    class Meta(UserRecipeAdddateModel.Meta):
        default_related_name = 'favorites'
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'

    def __str__(self) -> str:
        return f'{self.user} любит {self.recipe}'


class ShoppingCart(UserRecipeAdddateModel):

    class Meta(UserRecipeAdddateModel.Meta):
        default_related_name = 'shoppingcarts'
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'


class IngredientAmount(models.Model):
    recipe = models.ForeignKey(
        verbose_name='Рецепт',
        to=Recipe,
        related_name='ingredientamounts',
        on_delete=models.CASCADE,
    )
    ingredient = models.ForeignKey(
        verbose_name='Ингридиент',
        to=Ingredient,
        related_name='ingredientamounts',
        on_delete=models.CASCADE,
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        default=1,
        validators=[
            MaxValueValidator(
                MAX_SCORE,
                f'Количество не более {MAX_SCORE}'
            ),
            MinValueValidator(
                MIN_SCORE,
                f'Количество не менее {MIN_SCORE}'
            )
        ],
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
                name='unique_recipe_ingredient',
            ),
        )

    def __str__(self) -> str:
        return f'{self.ingredient} в количестве {self.amount}.'
