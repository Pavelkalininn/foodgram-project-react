from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import User, Ingredient, Recipe, Tag, IngredientName


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = User


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
        queryset=Ingredient.objects.all(),
        slug_field='name'
    )
    measurement_unit = serializers.SlugRelatedField(
        queryset=Ingredient.objects.all(),
        slug_field='measurement_unit'
    )

    class Meta:
        fields = '__all__'
        model = Ingredient


class RecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    tags = TagSerializer(many=True, required=True)
    author = UserSerializer(required=True)
    ingredients = IngredientSerializer(many=True, required=True)

    class Meta:
        fields = '__all__'
        model = Recipe
