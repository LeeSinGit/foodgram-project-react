from django.contrib import admin
from django.db.models import Count

from .models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredients,
    ShoppingCart,
    Tag,
)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_display_links = ['name']
    search_fields = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')
    list_display_links = ['name']
    search_fields = ('name', 'slug')


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'favorited_count')
    list_display_links = ['name']
    list_filter = ('author', 'tags')
    search_fields = ('name', 'author__username')
    readonly_fields = ('favorited_count',)

    def get_queryset(self, request):
        queryset = super().get_queryset(
            request
        ).select_related(
            'author'
        ).prefetch_related(
            'ingredients', 'tags'
        )
        return queryset.annotate(
            favorited_count=Count('in_favorite')
        )

    def favorited_count(self, obj):
        return obj.favorited_count

    favorited_count.short_description = 'Количество в избранном'


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    list_display_links = ['user']
    list_filter = ('user', 'recipe')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    list_display_links = ['user']
    list_filter = ('user', 'recipe')


@admin.register(RecipeIngredients)
class RecipeIngredientsAdmin(admin.ModelAdmin):
    pass
