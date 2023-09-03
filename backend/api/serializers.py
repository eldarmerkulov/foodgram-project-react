from django.db import models
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers, status
from rest_framework.validators import UniqueValidator

import sys
from os import path
__path__ = path.dirname(path.abspath(__file__))
__parent__ = path.abspath(path.join(__path__, ".."))
sys.path.append(__parent__)
from recipes.models import Ingredient, IngredientAmount, Recipe, Tag
from users.models import Subscribe, User


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'
        read_only_fields = ('__all__',)


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'
        read_only_fields = ('__all__',)


class RecipeSerializerShort(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = 'id', 'name', 'image', 'cooking_time'
        read_only_fields = ('__all__',)


class CreateUserSerializer(UserCreateSerializer):
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())])
    username = serializers.CharField(
        validators=[UniqueValidator(queryset=User.objects.all())])

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'password',
            'username',
            'first_name',
            'last_name'
        )
        extra_kwargs = {
            'email': {'required': True},
            'username': {'required': True},
            'password': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }


class UserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Subscribe.objects.filter(
            user=user, author=obj.id
        ).exists()


class SubscribeSerializer(UserSerializer):
    recipes_count = serializers.SerializerMethodField()
    recipes = RecipeSerializerShort(many=True, read_only=True)

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('recipes_count', 'recipes')
        read_only_fields = (
            'email',
            'username',
            'first_name',
            'last_name'
        )

    def validate(self, data):
        author_id = self.context.get(
            'request'
        ).parser_context.get('kwargs').get('id')
        author = get_object_or_404(User, id=author_id)
        user = self.context.get('request').user
        if user.authors.filter(author=author_id).exists():
            raise serializers.ValidationError(
                detail='Подписка уже существует',
                code=status.HTTP_400_BAD_REQUEST,
            )
        if user == author:
            raise serializers.ValidationError(
                detail='Нельзя подписаться на самого себя',
                code=status.HTTP_400_BAD_REQUEST,
            )
        return data

    def get_is_subscribed(*args):
        return True

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class RecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    tags = TagSerializer(read_only=True, many=True)
    author = UserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorite = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    cooking_time = serializers.IntegerField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorite',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')

    def get_ingredients(self, recipe):
        ingredients = recipe.ingredients.values(
            'id', 'name', 'measurement_unit', amount=models.F('recipe__amount')
        )
        return ingredients

    def get_is_favorite(self, recipe):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.favorites.filter(recipe=recipe).exists()

    def get_is_in_shopping_cart(self, recipe):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.shoppingcarts.filter(recipe=recipe).exists()

    def validate(self, data):
        ingredients = self.initial_data.get('ingredients')
        tags = self.initial_data.get('tags')
        cooking_time = self.initial_data.get('cooking_time')
        if not ingredients:
            raise serializers.ValidationError({
                'ingredients': 'Должен быть хотя бы один ингредиент'
            })
        ingredients_check = []
        for object in ingredients:
            ingredient = get_object_or_404(
                Ingredient,
                id=object['id']
            )
            if ingredient in ingredients_check:
                raise serializers.ValidationError(
                    'Ингредиенты должны быть уникальными'
                )
            if int(object['amount']) < 0:
                raise serializers.ValidationError({
                    'ingredients': 'Количество должно быть больше 0'
                })
            ingredients_check.append(ingredient)
        for tag in tags:
            if not Tag.objects.filter(id=tag).exists():
                raise serializers.ValidationError(
                    'Указанного тега не существует'
                )
        if cooking_time < 1:
            raise serializers.ValidationError(
                'Время готовки должно быть не меньше одной минуты')
        data['ingredients'] = ingredients
        data['tags'] = tags
        data['cooking_time'] = cooking_time
        return data

    @staticmethod
    def create_recipe_ingredients(recipe, ingredients):
        ingredients_in_recipe = []

        for ingredient in ingredients:
            ingredients_in_recipe.append(
                IngredientAmount(
                    recipe=recipe,
                    ingredient_id=ingredient.get('id'),
                    amount=ingredient.get('amount')
                )
            )
        IngredientAmount.objects.bulk_create(ingredients_in_recipe)

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_recipe_ingredients(recipe, ingredients)
        return recipe

    def update(self, recipe, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        for key, value in validated_data.items():
            if hasattr(recipe, key):
                setattr(recipe, key, value)
        if tags:
            recipe.tags.clear()
            recipe.tags.set(tags)
        if ingredients:
            recipe.ingredients.clear()
            self.create_recipe_ingredients(recipe, ingredients)
        recipe.save()
        return recipe
