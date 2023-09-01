from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer, SerializerMethodField

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.shortcuts import get_object_or_404

from api.config.config import COOKING_TIME, ONE_OR_MORE_INGREDIENTS
from api.utils.serializers_utils import (
    is_recipe_favorited,
    is_recipe_in_shopping_cart,
    validate_tags,
    validate_unique_ingredients,
)
from baseapp.models import Ingredient, Recipe, RecipeIngredients, Tag
from users.models import Subscription


User = get_user_model()


class MiniRecipeSerializer(ModelSerializer):
    """Укороченный сериализатор для модели Recipe."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class UserSerializer(ModelSerializer):
    """Сериализатор для модели User."""

    is_subscribed = SerializerMethodField()
    recipes = MiniRecipeSerializer(many=True, read_only=True)
    recipes_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'password',
            'recipes',
            'recipes_count',
        )
        extra_kwargs = {'password': {'write_only': True}}
        read_only_fields = ('is_subscribed', 'recipes')

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        current_user = request.user if request else None

        if current_user and current_user.is_authenticated:
            return Subscription.objects.filter(
                user=current_user.id,
                author=obj.id
            ).exists()

        return False

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        current_user = request.user if request else None

        if current_user and current_user.is_authenticated:
            return Subscription.objects.filter(
                user=current_user.id,
                author=obj.id
            ).exists()

        return False

    def to_representation(self, instance: User) -> dict:
        """
        Преобразует модель пользователя в представление.
        """
        representation = super().to_representation(instance)

        recipes = MiniRecipeSerializer(
            instance.recipes.all(), many=True, context=self.context
        )

        representation['recipes'] = recipes.data

        return representation


class SubscriptionSerializer(UserSerializer):
    """Сериализатор для списка подписок пользователя."""

    recipes = MiniRecipeSerializer(many=True, read_only=True)
    recipes_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = User
        fields = (
            'recipes_count',
            'recipes',
            'is_subscribed',
            'last_name',
            'first_name',
            'username',
            'email',
            'id'
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            current_user = request.user
            return Subscription.objects.filter(
                user=current_user,
                author=obj
            ).exists()
        return False

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.query_params.get('recipes_limit')
        recipes = obj.recipes.all()
        if limit:
            recipes = recipes[:int(limit)]
        serializer = RecipeSerializer(
            recipes,
            many=True,
            read_only=True
        )
        return serializer.data


class TagSerializer(ModelSerializer):
    """Сериализатор для модели Tag."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color')


class IngredientSerializer(ModelSerializer):
    """Сериализатор для модели Ingredient."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientsSerializer(serializers.ModelSerializer):
    """Сериализатор для модели RecipeIngredients."""

    id = serializers.IntegerField(source='ingredient_id')
    name = serializers.SerializerMethodField(method_name='get_name')
    measurement_unit = serializers.SerializerMethodField(
        method_name='get_measurement_unit'
    )

    class Meta:
        model = RecipeIngredients
        fields = ('id', 'name', 'measurement_unit', 'amount')

    def get_name(self, obj) -> str:
        """Получает название ингредиента."""
        return obj.ingredient.name

    def get_measurement_unit(self, obj) -> str:
        """Получает единицу измерения ингредиента."""
        return obj.ingredient.measurement_unit


class CreateUpdateRecipeIngredientsSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Ingredient,
    позволяющий создавать, обновлять ингридиенты.
    """

    id = serializers.IntegerField()
    amount = serializers.IntegerField(
        validators=(
            MinValueValidator(
                1,
                message=ONE_OR_MORE_INGREDIENTS
            ),
        )
    )

    class Meta:
        model = Ingredient
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Recipe."""

    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True)
    ingredients = serializers.SerializerMethodField(
        method_name='get_ingredients'
    )
    is_favorited = serializers.SerializerMethodField(
        method_name='get_is_favorited'
    )
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name='get_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'author',
            'image',
            'text',
            'ingredients',
            'tags',
            'cooking_time',
            'is_favorited',
            'is_in_shopping_cart',
        )

    def get_ingredients(self, obj) -> list:
        """Получает список ингредиентов для рецепта."""
        ingredients = RecipeIngredients.objects.filter(recipe=obj)
        serializer = RecipeIngredientsSerializer(ingredients, many=True)
        return serializer.data

    def get_is_favorited(self, obj):
        """Проверяет, добавлен ли рецепт в избранное пользователем."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            user = request.user
            return is_recipe_favorited(user, obj)
        return False

    def get_is_in_shopping_cart(self, obj):
        """Проверяет, добавлен ли рецепт в список покупок пользователя."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            current_user = request.user
            return is_recipe_in_shopping_cart(current_user, obj)
        return False


class RecipeCreateUpdateSerializer(ModelSerializer):
    """
    Сериализатор для модели Recipe,
    позволяющий создавать, обновлять рецепты.
    """

    author = UserSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    ingredients = CreateUpdateRecipeIngredientsSerializer(many=True)
    image = Base64ImageField()
    cooking_time = serializers.IntegerField(
        validators=(
            MinValueValidator(
                1,
                message=COOKING_TIME
            ),
        )
    )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'author',
            'image',
            'text',
            'ingredients',
            'tags',
            'cooking_time',
            'is_favorited',
            'is_in_shopping_cart',
        )

    def validate_tags(self, value) -> list:
        """Проверяет, что список тегов не пуст."""
        return validate_tags(value)

    def validate_ingredients(self, value) -> list:
        """Проверяет, что ингредиенты уникальны."""
        return validate_unique_ingredients(value)

    def create(self, validated_data: dict) -> Recipe:
        """
        Создает рецепт.

        Args:
            validated_data (dict): Проверенные данные.

        Returns:
            Recipe: Созданный рецепт.
        """
        author = self.context.get('request').user
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')

        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.tags.set(tags)

        for ingredient in ingredients:
            amount = ingredient['amount']
            ingredient = get_object_or_404(Ingredient, pk=ingredient['id'])

            RecipeIngredients.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                amount=amount
            )

        return recipe

    def update(self, recipe, validated_data):
        """
        Обновляет рецепт.

        Args:
            recipe (Recipe): Существующий рецепт.
            validated_data (dict): Проверенные данные.

        Returns:
            Recipe: Обновленный рецепт.
        """
        if 'ingredients' in validated_data:
            ingredients = validated_data.pop('ingredients')
            RecipeIngredients.objects.filter(recipe=recipe).delete()
            self.add_recipe_ingredients(ingredients, recipe)
        if 'tags' in validated_data:
            tags_data = validated_data.pop('tags')
            recipe.tags.set(tags_data)
        return super().update(recipe, validated_data)

    def add_recipe_ingredients(self, ingredients, recipe):
        """
        Добавляет ингредиенты к рецепту.

        Args:
            ingredients (list): Список ингредиентов.
            recipe (Recipe): Рецепт.
        """
        for ingredient in ingredients:
            ingredient_id = ingredient['id']
            amount = ingredient['amount']
            ingredient_instance = get_object_or_404(
                Ingredient,
                pk=ingredient_id
            )

            if RecipeIngredients.objects.filter(
                    recipe=recipe,
                    ingredient=ingredient_instance,
            ).exists():
                current_amount = RecipeIngredients.objects.get(
                    recipe=recipe,
                    ingredient=ingredient_instance
                ).amount
                new_amount = current_amount + amount
                if new_amount > 0:
                    RecipeIngredients.objects.update_or_create(
                        recipe=recipe,
                        ingredient=ingredient_instance,
                        defaults={'amount': new_amount},
                    )
                else:
                    RecipeIngredients.objects.filter(
                        recipe=recipe,
                        ingredient=ingredient_instance
                    ).delete()
            else:
                RecipeIngredients.objects.update_or_create(
                    recipe=recipe,
                    ingredient=ingredient_instance,
                    defaults={'amount': amount},
                )

    def to_representation(self, instance) -> dict:
        """
        Преобразует рецепт в представление.

        Args:
            instance (Recipe): Рецепт.

        Returns:
            dict: Представление рецепта.
        """
        serializer = RecipeSerializer(
            instance,
            context={'request': self.context.get('request')}
        )

        return serializer.data
