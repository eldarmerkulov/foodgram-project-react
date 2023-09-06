from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
)
from django.db import models
from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers, status

from core.constant import MAX_SCORE, MIN_SCORE
from recipes.models import (
    Ingredient,
    Favorite,
    IngredientAmount,
    Recipe,
    ShoppingCart,
    Tag
)
from users.models import User


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


class UserSerializer(serializers.ModelSerializer):
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
        return (
            user.authors.filter(author=obj).exists()
            and user.is_authenticated
        )


class SubscribeSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + (
            'recipes',
            'recipes_count'
        )
        read_only_fields = (
            'email',
            'username',
            'first_name',
            'last_name'
        )

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        queryset = obj.recipes.all()
        if limit:
            queryset = queryset[:int(limit)]
        serializer = RecipeSerializer(
            queryset,
            many=True,
            read_only=True
        )
        return serializer.data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class SubscribeCreateSerializer(SubscribeSerializer):
    author = serializers.PrimaryKeyRelatedField(
        read_only=True,
        many=True
    )
    user = serializers.PrimaryKeyRelatedField(
        read_only=True,
        many=True
    )

    class Meta(UserSerializer.Meta):
        fields = ('user', 'author')

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

    def to_representation(self, instance):
        context = {'request': self.context.get('request')}
        return SubscribeSerializer(
            instance,
            context=context
        ).data


class IngredientAmountSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        read_only=True,
        many=True
    )
    amount = serializers.IntegerField(
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
        model = IngredientAmount
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    cooking_time = serializers.IntegerField(
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
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class RecipeGetSerializer(RecipeSerializer):
    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorite = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta(RecipeSerializer.Meta):
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorite',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_ingredients(self, recipe):
        ingredients = recipe.ingredients.values(
            'id',
            'name',
            'measurement_unit',
            amount=models.F('ingredientamounts__amount')
        )
        return ingredients

    def get_is_favorite(self, recipe):
        user = self.context.get('request').user
        return (
            user.favorites.filter(recipe=recipe).exists()
            and user.is_authenticated
        )

    def get_is_in_shopping_cart(self, recipe):
        user = self.context.get('request').user
        return (
            user.shoppingcarts.filter(recipe=recipe).exists()
            and user.is_authenticated
        )


class RecipePostSerializer(RecipeSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        read_only=True,
        many=True
    )
    ingredients = IngredientAmountSerializer(
        read_only=True,
        many=True
    )

    class Meta(RecipeSerializer.Meta):
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
        )

    def validate(self, validated_data):
        ingredients = self.initial_data.get('ingredients')
        image = self.initial_data.get('image')
        tags = self.initial_data.get('tags')
        if not tags:
            raise serializers.ValidationError({
                'ingredients': 'Должен быть хотя бы один тэг'
            })
        if not ingredients:
            raise serializers.ValidationError({
                'ingredients': 'Должен быть хотя бы один ингредиент'
            })
        ingredients_check = [
            get_object_or_404(
                Ingredient,
                id=ingredient['id']
            ) for ingredient in ingredients
        ]

        if len(ingredients_check) > len(set(ingredients_check)):
            raise serializers.ValidationError(
                'Ингредиенты должны быть уникальными'
            )
        if not image:
            raise serializers.ValidationError({
                'ingredients': 'Добавьте изображение'
            })
        validated_data['tags'] = tags
        validated_data['ingredients'] = ingredients
        validated_data['image'] = image
        return validated_data

    @staticmethod
    def create_recipe_ingredients(recipe, ingredients):
        ingredients_in_recipe = [
            IngredientAmount(
                recipe=recipe,
                ingredient=Ingredient.objects.get(id=ingredient['id']),
                amount=ingredient['amount']
            ) for ingredient in ingredients
        ]
        IngredientAmount.objects.bulk_create(ingredients_in_recipe)

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(
            author=self.context.get('request').user,
            **validated_data)
        recipe.tags.set(tags)
        self.create_recipe_ingredients(recipe, ingredients)
        return recipe

    def update(self, recipe, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = super().update(recipe, validated_data)
        recipe.tags.clear()
        recipe.tags.set(tags)
        recipe.ingredients.clear()
        self.create_recipe_ingredients(recipe=recipe, ingredients=ingredients)
        recipe.save()
        return recipe

    def to_representation(self, instance):
        return RecipeGetSerializer(
            instance,
            context=self.context
        ).data


class ShoppingCartFavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('user', 'recipe')

    def validate(self, data):
        user, recipe = data.get('user'), data.get('recipe')
        if self.Meta.model.objects.filter(
                user=user,
                recipe=recipe
        ).exists():
            raise serializers.ValidationError(
                {'error': 'Этот рецепт уже добавлен'}
            )
        return data

    def to_representation(self, instance):
        context = {'request': self.context.get('request')}
        return RecipeSerializer(
            instance.recipe,
            context=context
        ).data


class FavoriteSerializer(ShoppingCartFavoriteSerializer):
    class Meta(ShoppingCartFavoriteSerializer.Meta):
        model = Favorite


class ShoppingCartSerializer(ShoppingCartFavoriteSerializer):
    class Meta(ShoppingCartFavoriteSerializer.Meta):
        model = ShoppingCart
