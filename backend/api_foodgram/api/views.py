import http

from django.contrib.auth.decorators import login_required
from django.http import FileResponse
from django_filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import api_view, action
from rest_framework.generics import get_object_or_404
from rest_framework.mixins import CreateModelMixin, ListModelMixin, \
    RetrieveModelMixin
from rest_framework.pagination import PageNumberPagination, \
    LimitOffsetPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from api.filters import RecipeFilter
from api.paginations import LargeResultsSetPagination
from api.serializers import (
    UserSerializer, TagSerializer, RecipeSerializer, IngredientSerializer,
    IngredientNameSerializer, SubscriptionSerializer, FavoriteSerializer,
    UserCreateSerializer
)
from recipes.models import User, Tag, Recipe, Ingredient, IngredientName


class UserViewSet(
    CreateModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    GenericViewSet,
):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = LargeResultsSetPagination

    @action(methods=['get'], detail=False)
    def me(self, request):
        if request.user.is_anonymous:
            return Response(
                status=status.HTTP_401_UNAUTHORIZED,
                data={"detail": "Учетные данные не были предоставлены."}
            )
        user = get_object_or_404(User, username=request.user.username)

        serializer = self.get_serializer(user)
        return Response(serializer.data)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UserCreateSerializer
        return UserSerializer

    def get_permissions(self):
        print(self.kwargs.get('pk'))
        if self.action == 'me' or self.kwargs.get('pk'):
            return (IsAuthenticated(),)
        return (AllowAny(), )


class TagViewSet(
    ListModelMixin,
    RetrieveModelMixin,
    GenericViewSet
):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = LargeResultsSetPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    filterset_fields = ('tags', 'author')


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
        subscriptions = [
            sub.user for sub in user.subscription_from_author.all()
        ]
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
