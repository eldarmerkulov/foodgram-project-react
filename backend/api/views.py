import io

from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet as BaseUserViewSet
from django_filters.rest_framework import DjangoFilterBackend
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly
)
from rest_framework.response import Response

from .filters import IngredientFilter, RecipeFilter
from .paginators import PageLimitPagination
from .permissions import IsAdminOrAuthorOrReadOnly
from .serializers import (
    IngredientSerializer,
    FavoriteSerializer,
    RecipeGetSerializer,
    RecipePostSerializer,
    ShoppingCartSerializer,
    SubscribeCreateSerializer,
    SubscribeSerializer,
    TagSerializer,
)
from recipes.models import (
    Ingredient,
    IngredientAmount,
    Favorite,
    Recipe,
    ShoppingCart,
    Tag
)
from users.models import Subscribe, User


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class UserViewSet(BaseUserViewSet):
    queryset = User.objects.all()
    serializer_class = SubscribeSerializer
    pagination_class = PageLimitPagination
    permission_classes = (IsAuthenticatedOrReadOnly,)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=(IsAuthenticated,),
    )
    def subscribe(self, request, id):
        serializer = SubscribeCreateSerializer(
            data={
                'user': request.user.id,
                'author': id
            },
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    @subscribe.mapping.delete
    def delete_subscribe(self, request, id):
        get_object_or_404(
            Subscribe,
            user=request.user,
            author=get_object_or_404(User, pk=id)
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request):
        queryset = self.paginate_queryset(
            User.objects.filter(subscribers__user=request.user)
        )
        serializer = SubscribeSerializer(
            queryset,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.select_related(
        'author'
    ).prefetch_related('tags', 'ingredients')
    pagination_class = PageLimitPagination
    permission_classes = (IsAdminOrAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeGetSerializer
        return RecipePostSerializer

    @action(
        detail=True,
        methods=['post'],
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk):
        return self.add_obj(FavoriteSerializer, request, pk)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk):
        return self.delete_obj(Favorite, request, pk)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk):
        return self.add_obj(ShoppingCartSerializer, request, pk)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk):
        return self.delete_obj(ShoppingCart, request, pk)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        ingredients = IngredientAmount.objects.filter(
            recipe__shoppingcarts__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit',
        ).annotate(amount=Sum('amount')).order_by('ingredient__name')
        pdf_file = self.create_pdf(ingredients)
        return FileResponse(
            pdf_file,
            as_attachment=True,
            filename='shopping_list.pdf'
        )

    @staticmethod
    def create_pdf(ingredients):
        pdfmetrics.registerFont(
            TTFont('ArialRegular', 'ArialRegular.ttf', 'UTF-8')
        )
        buffer = io.BytesIO()
        page = canvas.Canvas(buffer)
        page.setFont('ArialRegular', size=22)
        page.drawString(200, 800, 'Список ингредиентов')
        height = 750
        page.setFont('ArialRegular', size=12)
        for i, ingredient in enumerate(ingredients, 1):
            page.drawString(
                75, height, (
                    f'{i}) '
                    f'{ingredient["ingredient__name"].capitalize()} - '
                    f'{ingredient["amount"]} '
                    f'{ingredient["ingredient__measurement_unit"]}'
                )
            )
            height -= 25
        page.showPage()
        page.save()
        buffer.seek(0)
        return buffer

    @staticmethod
    def add_obj(serializer_class, request, pk):
        serializer = serializer_class(
            data={'user': request.user.id, 'recipe': pk},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    @staticmethod
    def delete_obj(model, request, pk):
        obj = model.objects.filter(
            user=request.user,
            recipe=get_object_or_404(Recipe, pk=pk)
        )
        if obj.exists():
            obj.delete()
            return Response(
                status=status.HTTP_204_NO_CONTENT
            )
        return Response(
            {
                'error': 'Рецепт уже удален'
            },
            status=status.HTTP_400_BAD_REQUEST
        )
