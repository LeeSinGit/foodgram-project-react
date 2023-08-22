from distutils.util import strtobool
from typing import Any

from django_filters import rest_framework as filters

from django.db import models

from baseapp.models import Favorite, Recipe, ShoppingCart, Tag


class RecipeFilter(filters.FilterSet):
    class IsFavoritedChoices(models.TextChoices):
        FALSE = '0', 'False'
        TRUE = '1', 'True'

    is_favorited = filters.ChoiceFilter(
        choices=IsFavoritedChoices.choices,
        method='is_favorited_method'
    )

    class IsInShoppingCartChoices(models.TextChoices):
        FALSE = '0', 'False'
        TRUE = '1', 'True'

    is_in_shopping_cart = filters.ChoiceFilter(
        choices=IsInShoppingCartChoices.choices,
        method='is_in_shopping_cart_method'
    )

    author = filters.NumberFilter(
        field_name='author',
        lookup_expr='exact'
    )
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )

    def is_favorited_method(self, queryset: Any, name: str, value: str) -> Any:
        """
        Фильтр по избранности рецепта.

        Args:
            queryset (QuerySet): Исходный набор данных.
            name (str): Имя поля фильтра.
            value (str): Значение фильтра.

        Returns:
            QuerySet: Отфильтрованный набор данных.
        """
        if self.request.user.is_anonymous:
            return Recipe.objects.none()

        favorites = Favorite.objects.filter(user=self.request.user)
        recipe_ids = favorites.values_list('recipe__id', flat=True)

        if not strtobool(value):
            return queryset.exclude(id__in=recipe_ids)

        return queryset.filter(id__in=recipe_ids)

    def is_in_shopping_cart_method(
            self,
            queryset: Any,
            name: str,
            value: str
    ) -> Any:
        """
        Фильтр по наличию в списке покупок.

        Args:
            queryset (QuerySet): Исходный набор данных.
            name (str): Имя поля фильтра.
            value (str): Значение фильтра.

        Returns:
            QuerySet: Отфильтрованный набор данных.
        """
        class Meta:
            model = Recipe
            fields = ('author', 'tags')

        if self.request.user.is_anonymous:
            return Recipe.objects.none()

        shopping_cart = ShoppingCart.objects.filter(user=self.request.user)
        recipe_ids = shopping_cart.values_list('recipe__id', flat=True)

        if not strtobool(value):
            return queryset.exclude(id__in=recipe_ids)

        return queryset.filter(id__in=recipe_ids)
