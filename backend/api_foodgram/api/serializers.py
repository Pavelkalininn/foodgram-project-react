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
    name = serializers.SlugRelatedField(
        # queryset=IngredientName.objects.all(),
        slug_field='ingredient_name__name',
        read_only=True
    )
    measurement_unit = serializers.SlugRelatedField(
        # queryset=IngredientName.objects.all(),
        slug_field='ingredient_name__measurement_unit',
        read_only=True
    )

    class Meta:
        fields = 'amount', 'ingredient_name', 'name', 'measurement_unit'
        model = Ingredient


class RecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    tags = TagSerializer(many=True, required=True)
    # author = UserSerializer(required=True)
    ingredients = serializers.SlugRelatedField('name', read_only=True)

    class Meta:
        fields = '__all__'
        model = Recipe
