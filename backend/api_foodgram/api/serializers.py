from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.mixins import CreateModelMixin, ListModelMixin, \
    RetrieveModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from recipes.models import (
    User,
    Ingredient,
    Recipe,
    Tag,
    IngredientName,
    Subscription,
    Favorite,
    ShoppingCart,
)


class UserCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'username',
            'first_name',
            'last_name'
        ]


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        parent_fields = list(UserCreateSerializer.Meta.fields)
        parent_fields.append('is_subscribed')
        fields = parent_fields

    def get_is_subscribed(self, obj):
        if Subscription.objects.filter(
                user=obj.id,
                author=self.context.get('request').user.id
        ).exists():
            return True
        return False


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Tag


class IngredientNameSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = IngredientName


class IngredientSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    measurement_unit = serializers.SerializerMethodField()

    class Meta:
        fields = 'id', 'amount', 'name', 'measurement_unit'
        model = Ingredient

    def get_name(self, obj):
        return obj.ingredient_name.name

    def get_measurement_unit(self, obj):
        return obj.ingredient_name.measurement_unit


class RecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = IngredientSerializer(many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        fields = '__all__'
        model = Recipe

    def get_is_favorited(self, obj):
        return Favorite.objects.filter(
                author=self.context.get('request').user.id,
                recipe=obj.id
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        return ShoppingCart.objects.filter(
                author=self.context.get('request').user.id,
                recipe=obj.id
        ).exists()


class SubscriptionRecipeSerializer(RecipeSerializer):

    class Meta:
        fields = 'id', 'name', 'image', 'cooking_time'
        model = Recipe


class SubscriptionSerializer(UserSerializer):
    recipes = SubscriptionRecipeSerializer(many=True)
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )
        model = User

    def get_recipes_count(self, obj):
        return obj.recipes.all().count()


class FavoriteSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        fields = 'id', 'name', 'image', 'cooking_time'
        model = Recipe
