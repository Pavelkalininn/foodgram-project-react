from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import SAFE_METHODS

from api_foodgram.settings import (ALREADY_CREATED, COOKING_TIME_LIMIT,
                                   FRIENDLY_FIRE, HAVE_NOT_OBJECT_FOR_DELETE,
                                   ID_NOT_FOUND, IS_A_POSITIVE_INT,
                                   UNIQUE_TOGETHER_EXCEPTION)
from recipes.models import (Favorite, Ingredient, IngredientName, Recipe,
                            ShoppingCart, Subscription, Tag, User)


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
        return Subscription.objects.filter(
            user=obj.id,
            author=self.context.get('request').user.id
        ).exists()


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


class IngredientCreateSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=IngredientName.objects.all(),
    )
    amount = serializers.IntegerField()

    class Meta:
        fields = 'id', 'amount'
        model = Ingredient


class RecipeReadSerializer(serializers.ModelSerializer):
    image = Base64ImageField(max_length=None, use_url=True)
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


class RecipeCreateSerializer(serializers.ModelSerializer):
    image = Base64ImageField(max_length=None, use_url=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    author = UserSerializer(default=serializers.CurrentUserDefault())
    ingredients = IngredientCreateSerializer(many=True)

    class Meta:
        fields = '__all__'
        model = Recipe

    def validate_cooking_time(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                IS_A_POSITIVE_INT.format(name='время приготовления')
            )
        return value

    def validate_ingredients(self, value):
        ingredient_ids = [
            ingredient.get('id').id
            for ingredient in value
        ]
        if IngredientName.objects.filter(
                id__in=ingredient_ids
        ).count() != len(value):
            raise serializers.ValidationError(
                ID_NOT_FOUND.format(name='ингредиент')
            )
        return value

    def validate(self, obj):
        request = self.context.get('request')
        if request.method not in SAFE_METHODS:
            if obj.get('name'):
                if Recipe.objects.filter(
                        author=request.user,
                        name=obj.get('name')
                ).exists():
                    raise serializers.ValidationError(
                        ALREADY_CREATED.format(name='рецепт')
                    )
        return obj

    def ingredients_create(self, ingredients_data):
        ingredients = []
        for ingredient in ingredients_data:
            ingredient_name = get_object_or_404(
                IngredientName,
                id=ingredient.get('id').id
            )
            ingredient, _ = Ingredient.objects.get_or_create(
                ingredient_name=ingredient_name,
                amount=ingredient.get('amount'),
            )
            ingredients.append(ingredient)
        # Для many to many мне нужно добавлять ингредиент через set,
        # а тут мне никто не возвращает id для такой привязки.
        # Привязать параметр recipes при создании объекта класса мне тоже не
        # позволяет, указывая на необходимость привязки параметра many to many
        # через set.
        # Если не привязывать ingredients к рецепту они, соответственно, не
        # привязываются.
        # Отдельной таблицы связывающей ингредиенты и рецепты у меня нет
        return ingredients

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        ingredients = self.ingredients_create(ingredients)
        recipe.ingredients.set(ingredients)
        return recipe

    def update(self, instance, validated_data):
        instance.tags.clear()
        tags = validated_data.pop('tags')
        instance.tags.set(tags)
        ingredients = validated_data.pop('ingredients')
        instance.ingredients.clear()
        ingredients = self.ingredients_create(ingredients)
        instance.ingredients.set(ingredients)
        return super().update(
            instance,
            validated_data
        )

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeReadSerializer(instance, context=context).data


class SubscriptionRecipeSerializer(RecipeReadSerializer):
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


class SubscriptionCreateSerializer(SubscriptionSerializer):
    author = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        fields = 'id', 'author', 'user'
        model = User

    def validate(self, obj):
        author = obj.get('author')
        user = obj.get('user')
        request = self.context.get('request')
        if author == user:
            raise ValidationError(FRIENDLY_FIRE)
        subscription_exists = Subscription.objects.filter(
            author=author,
            user=user
        ).exists()
        if request.method == "POST":
            if subscription_exists:
                raise ValidationError(
                    ALREADY_CREATED.format(name='подписчик')
                )
        else:
            if not subscription_exists:
                raise ValidationError(
                    {'errors': HAVE_NOT_OBJECT_FOR_DELETE.format(
                        name='Подписка')
                    }
                )
        return obj


class SubscriptionsGetSerializer(SubscriptionSerializer):
    author = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    recipes_limit = serializers.IntegerField(allow_null=True)

    class Meta:
        fields = 'id', 'author', 'recipes_limit'
        model = User

    def validate_recipes_limit(self, value):
        if value and value <= 0:
            raise ValidationError(
                IS_A_POSITIVE_INT.format(name='recipes_limit')
            )
        return value


class ShoppingCartSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())

    class Meta:
        fields = 'author', 'recipe'
        model = ShoppingCart

    def validate(self, obj):
        author = obj.get('author')
        recipe = obj.get('recipe')
        model_class = self.context.get('model_class')
        request = self.context.get('request')
        if request.method == 'POST':
            if model_class.objects.filter(
                    author=author,
                    recipe=recipe
            ).exists():
                raise ValidationError(
                    ALREADY_CREATED.format(name='рецепт')
                )
        else:
            if not model_class.objects.filter(
                    author=author,
                    recipe=recipe
            ).exists():
                raise ValidationError(
                    {'errors': HAVE_NOT_OBJECT_FOR_DELETE.format(name='Рецепт')
                     }
                )
        return obj
