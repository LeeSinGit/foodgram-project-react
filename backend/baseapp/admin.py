from django.contrib import admin
from django.contrib.admin import register

from .models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredients,
    ShoppingCart,
    Tag,
)


@register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit', )
    list_filter = ('name', )
    search_fields = ('id', 'name', )


@register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'color', 'slug', )
    search_fields = ('id', 'name', 'slug', )


@register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author')
    list_filter = ('author', 'name', 'tags')
    search_fields = ('name', 'author__username')
    readonly_fields = ('favorited_count',)

    def favorited_count(self, obj):
        return obj.is_favorited.count()

    favorited_count.short_description = 'Favorites Count'


@register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe',)
    list_filter = ('id', 'user', 'recipe')
    search_fields = ('id', 'name',)


@register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe',)
    list_filter = ('id', 'user', 'recipe',)
    search_fields = ('id', 'name',)


@register(RecipeIngredients)
class RecipeIngredientsAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipe', 'ingredient', 'amount')
    list_filter = ('id', 'recipe', 'ingredient', 'amount')
    search_fields = ('id', 'amount',)
