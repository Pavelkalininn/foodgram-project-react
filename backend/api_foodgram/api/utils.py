from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from api.serializers import SubscriptionRecipeSerializer
from api_foodgram.settings import (ALREADY_CREATED, ID_NOT_FOUND,
                                   IS_A_POSITIVE_INT)
from recipes.models import Recipe


def shopping_cart_data_creator(user):
    ingredients_count = {}
    for cart_objects in user.cart.all():
        for ingredient in cart_objects.recipe.ingredients.all():
            key = (
                    ingredient.ingredient_name.name
                    + ' ('
                    + ingredient.ingredient_name.measurement_unit
                    + ')'
            )
            if key in ingredients_count:
                ingredients_count[key] += ingredient.amount
            else:
                ingredients_count[key] = ingredient.amount
    cart_data = ''
    for key, value in ingredients_count.items():
        cart_data += (str(key) + ": " + str(value) + '\n')
    return cart_data


def cart_favorite_add_or_delete(
        recipe_id,
        request,
        model_class
):
    if not recipe_id.isnumeric() or int(recipe_id) <= 0:
        raise ValidationError(
            IS_A_POSITIVE_INT.format('рецепта')
        )
    if not Recipe.objects.filter(id=recipe_id).exists():
        raise ValidationError(
            {'errors': ID_NOT_FOUND.format(name='рецепт')}
        )
    recipe = get_object_or_404(Recipe, id=recipe_id)
    user = request.user
    if request.method == 'POST':
        if model_class.objects.filter(
                author=user,
                recipe=recipe
        ).exists():
            raise ValidationError(
                    ALREADY_CREATED.format(name='рецепт')
                )
        model_class.objects.create(
            author=user,
            recipe=recipe
        )
        serializer = SubscriptionRecipeSerializer(
            recipe,
            context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    if not model_class.objects.filter(
            author=user,
            recipe=recipe
    ).exists():
        raise ValidationError(
            {'errors': f'Этот рецепт не был добавлен и его невозможно удалить'}
        )
    current_object = get_object_or_404(
        model_class,
        author=user,
        recipe=recipe
    )
    current_object.delete()
    return Response(
        data={'detail': 'Рецепт успешно удалён'},
        status=status.HTTP_204_NO_CONTENT
    )
