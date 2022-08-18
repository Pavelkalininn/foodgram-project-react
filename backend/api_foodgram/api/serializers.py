from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from recipes.models import User, Ingredient, Recipe, Tag, IngredientName, \
    Subscription


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        ]

    def get_is_subscribed(self, obj):
        if Subscription.objects.filter(
                user=obj.id, author=self.context.get('request').user.id).all():
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

    class Meta:
        fields = '__all__'
        model = Recipe


class SubscriptionSerializer(UserSerializer):
    recipes = RecipeSerializer(many=True, read_only=True)

    class Meta:
        fields = 'id', 'email', 'username', 'first_name', 'last_name', 'is_subscribed', 'recipes'
        model = User


class FavoriteSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        fields = 'id', 'name', 'image', 'cooking_time'
        model = Recipe
