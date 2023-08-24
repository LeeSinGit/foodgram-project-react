from distutils.util import strtobool
from typing import Any

from baseapp.models import Favorite, Recipe, ShoppingCart, Tag
from django.db import models
from django_filters import rest_framework as filters


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

    class Meta:
        model = Recipe
        fields = ('author', 'tags')

    def is_favorited_method(self, queryset: Any, name: str, value: str) -> Any:
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
        if self.request.user.is_anonymous:
            return Recipe.objects.none()

        shopping_cart = ShoppingCart.objects.filter(user=self.request.user)
        recipe_ids = shopping_cart.values_list('recipe__id', flat=True)

        if not strtobool(value):
            return queryset.exclude(id__in=recipe_ids)

        return queryset.filter(id__in=recipe_ids)
