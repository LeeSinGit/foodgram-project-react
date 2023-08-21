from rest_framework import serializers

from api.config.config import AT_LEAST_ONE_TAG, IDENTICAL_ONES_ARE_NOT_ALLOWED
from baseapp.models import Favorite, ShoppingCart


def is_recipe_favorited(user, recipe):
    """
    Проверить, добавлен ли рецепт в избранное пользователем.

    Args:
        user (User): Пользователь.
        recipe (Recipe): Рецепт.

    Returns:
        bool: True, если рецепт добавлен в избранное пользователем,
        иначе False.
    """
    if user.is_anonymous:
        return False

    return Favorite.objects.filter(user=user, recipe=recipe).exists()


def is_recipe_in_shopping_cart(user, recipe):
    """
    Проверить, добавлен ли рецепт в список покупок пользователя.

    Args:
        user (User): Пользователь.
        recipe (Recipe): Рецепт.

    Returns:
        bool: True, если рецепт добавлен в список покупок пользователя,
        иначе False.
    """
    if user.is_anonymous:
        return False

    return ShoppingCart.objects.filter(user=user, recipe=recipe).exists()


def validate_tags(tags):
    """
    Проверить, что список тегов не пуст.

    Args:
        value (list): Список тегов.

    Raises:
        serializers.ValidationError: Если список тегов пуст.
    """
    if not tags:
        raise serializers.ValidationError(AT_LEAST_ONE_TAG)
    return tags


def validate_unique_ingredients(ingredients):
    """
    Проверить, что ингредиенты уникальны.

    Args:
        value (list): Список ингредиентов.

    Raises:
        serializers.ValidationError: Если есть дубликаты ингредиентов.
    """
    ingredient_ids = [item['id'] for item in ingredients]
    for ingredient in ingredient_ids:
        if ingredient_ids.count(ingredient) > 1:
            raise serializers.ValidationError(IDENTICAL_ONES_ARE_NOT_ALLOWED)
    return ingredients
