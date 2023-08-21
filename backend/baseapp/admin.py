from django.contrib import admin

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
    list_display = ('id', 'name', 'measurement_unit', )
    list_filter = ('name', )
    search_fields = ('id', 'name', )


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'color', 'slug', )
    search_fields = ('id', 'name', 'slug', )


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author')
    list_filter = ('author', 'name', 'tags')
    search_fields = ('name', 'author__username')
    readonly_fields = ('favorited_count',)

    def get_queryset(self, request):
        '''
        Используем select_related для заджойнивания авторов
        и зафетчивания ингредиентов и тегов
        '''
        queryset = super().get_queryset(
            request
        ).select_related(
            'author'
        ).prefetch_related(
            'ingredients',
            'tags'
        )
        return queryset

    def favorited_count(self, obj):
        return obj.is_favorited.count()

    favorited_count.short_description = 'Favorites Count'


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe',)
    list_filter = ('id', 'user', 'recipe')
    search_fields = ('id', 'name',)

    def get_queryset(self, request):
        '''
        Используем select_related для заджойнивания пользователей
        и зафетчивания связанных рецептов.
        '''
        queryset = super().get_queryset(
            request
        ).select_related(
            'user'
        ).prefetch_related(
            'recipe'
        )
        return queryset


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe',)
    list_filter = ('id', 'user', 'recipe',)
    search_fields = ('id', 'name',)

    def get_queryset(self, request):
        '''
        Используем select_related для заджойнивания пользователей
        и зафетчивания рецептов, находящихся в корзине.
        '''
        queryset = super().get_queryset(
            request
        ).select_related(
            'user'
        ).prefetch_related(
            'recipe'
        )
        return queryset


@admin.register(RecipeIngredients)
class RecipeIngredientsAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipe', 'ingredient', 'amount')
    list_filter = ('id', 'recipe', 'ingredient', 'amount')
    search_fields = ('id', 'amount',)

    def get_queryset(self, request):
        '''
        Используем select_related для заджойнивания рецептов
        и зафетчивания ингредиентов и их количества.
        '''
        queryset = super().get_queryset(
            request
        ).select_related(
            'recipe'
        ).prefetch_related(
            'ingredient',
            'amount'
        )
        return queryset
