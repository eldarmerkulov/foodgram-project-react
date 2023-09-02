from django.db import models
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

# Локальный импорт:
import sys
from os import path
__path__ = path.dirname(path.abspath(__file__))
__parent__ = path.abspath(path.join(__path__, ".."))
# Добавляем в sys-path именно parent, чтобы не слетала настройка в PyCharm
sys.path.append(__parent__)
from recipes.models import Ingredient, IngredientAmount, Recipe, ShoppingCart, Tag
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


class SubscribeSerializer(UserSerializer):
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


class RecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    tag = TagSerializer(read_only=True, many=True)
    author = UserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorite = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tag', 'author', 'ingredients', 'is_favorite',
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
        return Recipe.objects.filter(favorites__user=user, id=recipe.id).exists()

    def get_is_in_shopping_cart(self, recipe):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Recipe.objects.filter(cart__user=user, id=recipe.id).exists()

    def validate(self, data):
        ingredients = self.initial_data.get('ingredients')
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
        data['ingredients'] = ingredients
        return data

    def ingredients_in_recipe(self, recipe, ingredients):
        ingredients_in_recipe = []

        for ingredient, amount in ingredients.values():
            ingredients_in_recipe.append(
                IngredientAmount(
                    recipe=recipe, ingredients=ingredient, amount=amount
                )
            )
        IngredientAmount.objects.bulk_create(ingredients_in_recipe)

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.ingredients_in_recipe(recipe, ingredients)
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
            self.ingredients_in_recipe(recipe, ingredients)
        recipe.save()
        return recipe

# class UserSerializer(serializers.ModelSerializer):
#     username = serializers.CharField(
#         max_length=LENGTH_NAME_USER,
#         validators=[validators.UniqueValidator(queryset=User.objects.all())]
#     )
#     email = serializers.EmailField(
#         max_length=LENGTH_EMAIL,
#         validators=[validators.UniqueValidator(queryset=User.objects.all())]
#     )
#
#     class Meta:
#         fields = ('username', 'email', 'first_name', 'last_name',
#                   'bio', 'role')
#         model = User
#
#     def validate_username(self, username):
#         return validate_username(username)
#
#
# class UserMeSerializer(UserSerializer):
#     class Meta(UserSerializer.Meta):
#         read_only_fields = ('role',)
#
#
# class UserAuthSerializer(serializers.Serializer):
#     username = serializers.CharField(
#         max_length=LENGTH_NAME_USER,
#     )
#     email = serializers.EmailField(
#         max_length=LENGTH_EMAIL,
#     )
#
#     class Meta:
#         fields = ('username', 'email')
#
#     def validate_username(self, username):
#         return validate_username(username)
#
#     def validate(self, data):
#         username = data['username']
#         email = data['email']
#         existing_with_email = User.objects.filter(email=email).first()
#         if existing_with_email:
#             if existing_with_email.username != username:
#                 raise ValidationError('пользователь с таким email'
#                                       'уже существует')
#         existing_with_username = User.objects.filter(username=username).first()
#         if existing_with_username:
#             if existing_with_username.email != email:
#                 raise ValidationError('пользователь с таким username'
#                                       'уже существует')
#         return data
#
#     def create(self, validated_data):
#         user, _ = User.objects.get_or_create(**validated_data)
#         return user
#
#
# class GetTokenSerializer(serializers.ModelSerializer):
#     username = serializers.CharField(
#         max_length=LENGTH_NAME_USER,
#     )
#     confirmation_code = serializers.CharField(required=True)
#
#     class Meta:
#         fields = ('username', 'confirmation_code')
#         model = User
#
#     def validate_username(self, username):
#         return validate_username(username)
#
#
# class ReviewSerializer(serializers.ModelSerializer):
#     author = serializers.SlugRelatedField(
#         read_only=True, slug_field='username'
#     )
#
#     class Meta:
#         fields = ('id', 'text', 'author', 'score',
#                   'pub_date')
#         model = Review
#
#     def validate(self, data):
#         if self.context['request'].method == 'POST':
#             author = self.context['request'].user
#             title_id = self.context.get('view').kwargs.get('title_id')
#             if Review.objects.filter(
#                     author=author,
#                     title_id=title_id
#             ).exists():
#                 raise ValidationError("Нельзя оставлять два отзыва на одно"
#                                       "произведение!")
#         return data
#
#
# class CategorySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Category
#         fields = ('name', 'slug',)
#         lookup_field = 'slug'
#
#
# class CommentSerializer(serializers.ModelSerializer):
#     author = serializers.SlugRelatedField(
#         read_only=True, slug_field='username',
#     )
#
#     class Meta:
#         fields = ('id', 'text', 'author', 'pub_date')
#         model = Comment
#         read_only_fields = ('author', 'id', 'pub_date')
#
#
# class GenreSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Genre
#         fields = ('name', 'slug',)
#         lookup_field = 'slug'
#
#
# class TitleListSerializer(serializers.ModelSerializer):
#     genre = GenreSerializer(many=True, )
#     category = CategorySerializer()
#
#     rating = serializers.IntegerField(read_only=True)
#
#     class Meta:
#         fields = ('id', 'name', 'year', 'rating', 'description', 'genre',
#                   'category')
#         model = Title
#         read_only_fields = ('rating',)
#
#
# class TitleSerializer(serializers.ModelSerializer):
#     year = serializers.IntegerField()
#     genre = serializers.SlugRelatedField(
#         slug_field='slug', many=True,
#         queryset=Genre.objects.all()
#     )
#     category = serializers.SlugRelatedField(
#         slug_field='slug',
#         queryset=Category.objects.all()
#     )
#     rating = serializers.FloatField(read_only=True)
#
#     def validate_year(self, value):
#         return validate_year(value)
#
#     def validate_genre(self, value):
#         return validate_genre(value)
#
#     class Meta:
#         fields = ('id', 'name', 'year', 'rating', 'description', 'genre',
#                   'category')
#         model = Title
#         read_only_fields = ('rating',)
#
#     def to_representation(self, value):
#         return TitleListSerializer(value).data
