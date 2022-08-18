from django.contrib.auth.decorators import login_required
from django.http import FileResponse
from django.shortcuts import render
from rest_framework import filters, status, viewsets
from rest_framework.decorators import api_view, action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from api.serializers import (
    UserSerializer, TagSerializer, RecipeSerializer, IngredientSerializer,
    IngredientNameSerializer, SubscriptionSerializer, FavoriteSerializer
)
from recipes.models import User, Tag, Recipe, Ingredient, IngredientName


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(methods=['get'], detail=False)
    def me(self, request):
        user = User.objects.get(username=request.user.username)
        serializer = self.get_serializer(user)
        return Response(serializer.data)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    #  ВЫВЕСТИ
    # is_favorited = models.BooleanField(default=False)
    # is_in_shopping_cart = models.BooleanField(default=False)


class FavoriteViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = Recipe.objects.all()

    def perform_create(self, serializer):
        recipe_id = self.kwargs.get('recipe_id')
        recipe = get_object_or_404(Recipe, id=recipe_id)
        self.request.user.favorited.add(recipe)
        return self.request.user
        # serializer.save(
        #     author=self.request.user,
        #     recipe=recipe
        # )


class SubscriptionViewSet(viewsets.ModelViewSet):
    serializer_class = SubscriptionSerializer

    def get_queryset(self):
        user = get_object_or_404(
            User,
            id=self.request.user.pk
        )
        subscriptions = user.subscriptions.all()
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
    file = open('test.txt', 'w+')
    for key, value in shopping_cart.items():
        file.write(str(key) + ": " + str(value) + '\n')
    file.close()
    print('shopping_cart is empty')
    return FileResponse(
        open('test.txt', 'w+'),
        as_attachment=True,
        content_type='application/txt', filename='test.txt'
    )
