# Generated by Django 3.2.3 on 2023-09-02 21:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0005_alter_recipe_tag'),
    ]

    operations = [
        migrations.RenameField(
            model_name='recipe',
            old_name='tag',
            new_name='tags',
        ),
    ]
