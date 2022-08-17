from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import User, Ingredient, Recipe, Tag, IngredientName


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            'id',
            'subscriptions',
            'recipes',
            'favorited',
            'shopping_cart',
            'password'
        ]


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = Tag


class IngredientNameSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = IngredientName


class IngredientSerializer(serializers.ModelSerializer):
    ingredient_name = IngredientNameSerializer(read_only=True)
    name = serializers.SerializerMethodField()
    measurement_unit = serializers.SerializerMethodField()

    class Meta:
        fields = 'amount', 'ingredient_name'
        model = Ingredient

        def get_name(self):
            return self


class RecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    tags = TagSerializer(many=True, read_only=True)
    # author = UserSerializer(read_only=True)
    ingredients = IngredientSerializer(many=True, read_only=True)

    class Meta:
        fields = '__all__'
        model = Recipe
