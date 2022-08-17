from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from rest_framework import filters, status, viewsets
from rest_framework.decorators import api_view
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from api.serializers import (
    UserSerializer, TagSerializer, RecipeSerializer, IngredientSerializer,
    IngredientNameSerializer
)
from recipes.models import User, Tag, Recipe, Ingredient, IngredientName


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer


# class ShoppingCartViewSet(viewsets.ModelViewSet):
#     serializer_class = ShoppingCartSerializer
#
#     def get_queryset(self):
#         user = get_object_or_404(
#             User,
#             id=self.request.user.pk
#         )
#         shopping_cart = {}
#         for recipe in user.shopping_cart:
#             for ingredient in recipe.ingredients:
#                 key = ingredient.ingredient_name.name + ' ' + ingredient.ingredient_name.measurement_unit
#                 if key in shopping_cart:
#                     shopping_cart[key] += ingredient.amount
#                 else:
#                     shopping_cart[key] = ingredient.amount
#         return shopping_cart


class FavoriteViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeSerializer

    def get_queryset(self):
        user = get_object_or_404(
            User,
            id=self.request.user.pk
        )
        favorited = user.favorited
        return favorited


class SubscriptionViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer

    def get_queryset(self):
        user = get_object_or_404(
            User,
            id=self.request.user.pk
        )
        subscriptions = user.subscriptions
        return subscriptions


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class IngredientNameViewSet(viewsets.ModelViewSet):
    queryset = IngredientName.objects.all()
    serializer_class = IngredientNameSerializer


@api_view(['GET'])
# @login_required
def get_shopping_cart(request):
    user = get_object_or_404(
                User,
                id=request.user.pk
            )
    shopping_cart = {}

    for recipe in user.shopping_cart.all():
        for ingredient in recipe.ingredients.all():
            key = (
                    ingredient.ingredient_name.name
                    + ' '
                    + ingredient.ingredient_name.measurement_unit
            )

            if key in shopping_cart:
                shopping_cart[key] += ingredient.amount
            else:
                shopping_cart[key] = ingredient.amount
    print('shopping_cart is empty')
    return Response(status=status.HTTP_204_NO_CONTENT, data=shopping_cart, content_type='json')
