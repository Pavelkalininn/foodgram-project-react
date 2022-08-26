
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
        cart_data += str(key) + ": " + str(value) + '\n'
    return cart_data
