# Generated by Django 3.2.3 on 2023-09-05 10:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0007_auto_20230905_1254'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='favorite',
            name='favorite. Рецепт уже добавлен.',
        ),
        migrations.RemoveConstraint(
            model_name='ingredient',
            name='ingredient is already exists.',
        ),
        migrations.RemoveConstraint(
            model_name='ingredientamount',
            name='ingredient already added.',
        ),
        migrations.RemoveConstraint(
            model_name='shoppingcart',
            name='shoppingcart. Рецепт уже добавлен.',
        ),
        migrations.AddConstraint(
            model_name='favorite',
            constraint=models.UniqueConstraint(fields=('user', 'recipe'), name='favorite_unique_recipe_user'),
        ),
        migrations.AddConstraint(
            model_name='ingredient',
            constraint=models.UniqueConstraint(fields=('name', 'measurement_unit'), name='unique_ingredient_measurement_unit'),
        ),
        migrations.AddConstraint(
            model_name='ingredientamount',
            constraint=models.UniqueConstraint(fields=('recipe', 'ingredient'), name='unique_recipe_ingredient'),
        ),
        migrations.AddConstraint(
            model_name='shoppingcart',
            constraint=models.UniqueConstraint(fields=('user', 'recipe'), name='shoppingcart_unique_recipe_user'),
        ),
    ]
