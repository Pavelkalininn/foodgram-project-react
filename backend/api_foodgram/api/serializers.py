from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

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

    def validate_cooking_time(self, value):
        if value not in range(1, 1000):
            raise serializers.ValidationError(
                'Введите время приготовления от 1 до 1000'
            )
        return value

    def validate(self, obj):
        request = self.context.get('request')
        data = request.data
        tag_ids = data.get('tags')
        ingredient_ids = [
            ingredient.get('id')
            for ingredient in data.get('ingredients')
        ]
        if (
                Tag.objects.filter(id__in=tag_ids).count() != len(tag_ids)
                or IngredientName.objects.filter(
                id__in=ingredient_ids).count() != len(ingredient_ids)
        ):
            raise serializers.ValidationError(
                'Не найдено ингредиента или тэга с таким id'
            )

        if request.method == 'PATCH':
            if Recipe.objects.filter(
                    author=request.user,
                    name=data.get('name')
            ).exists():
                raise serializers.ValidationError(
                    'Ваш рецепт с таким названием уже есть.'
                )
        return obj


class SubscriptionRecipeSerializer(RecipeSerializer):
    class Meta:
        fields = 'id', 'name', 'image', 'cooking_time'
        model = Recipe


class SubscriptionSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField()
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
        return obj.recipes.count()

    def get_recipes(self, obj):
        recipes = obj.recipes.all()[:self.context.get('recipes_limit')]
        return SubscriptionRecipeSerializer(recipes, many=True).data
