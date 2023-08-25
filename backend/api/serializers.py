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

    def get_is_subscribed(self, obj: User) -> bool:
        """Проверяет, подписан ли пользователь."""
        user = self.context.get('request').user

        if user.is_anonymous:
            return False

        return obj.subscribers.filter(user=user).exists()

    def get_recipes_count(self, obj: User) -> int:
        """Получает количество рецептов определенного пользователя."""
        return obj.recipes_count

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

    def create(self, validated_data: dict) -> User:
        """
        Создать пользователя.

        Args:
            validated_data (dict): Проверенные данные.

        Returns:
            User: Созданный пользователь.
        """
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            password=validated_data['password']
        )
        return user


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

    def get_recipes_count(self, obj: User) -> int:
        """Получает количество рецептов определенного пользователя."""
        return obj.recipes_count


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
    """Сериализатор для модели RecipeIngredients"""

    id = serializers.IntegerField(source='ingredient_id')
    name = serializers.SerializerMethodField(method_name='get_name')
    measurement_unit = serializers.SerializerMethodField(
        method_name='get_measurement_unit'
    )

    def get_name(self, obj) -> str:
        """Получает название ингредиента."""
        return obj.ingredient.name

    def get_measurement_unit(self, obj) -> str:
        """Получает единицу измерения ингредиента."""
        return obj.ingredient.measurement_unit

    class Meta:
        model = RecipeIngredients
        fields = ('id', 'name', 'measurement_unit', 'amount')


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

    def get_ingredients(self, obj) -> list:
        """Получает список ингредиентов для рецепта."""
        ingredients = RecipeIngredients.objects.filter(recipe=obj)
        serializer = RecipeIngredientsSerializer(ingredients, many=True)
        return serializer.data

    def get_is_favorited(self, obj) -> bool:
        """Проверяет, добавлен ли рецепт в избранное пользователем."""
        user = self.context['request'].user
        return is_recipe_favorited(user, obj)

    def get_is_in_shopping_cart(self, obj) -> bool:
        """Проверяет, добавлен ли рецепт в список покупок пользователя."""
        user = self.context['request'].user
        return is_recipe_in_shopping_cart(user, obj)

    class Meta:
        model = Recipe
        exclude = ('pub_date',)


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

    def update(self, instance, validated_data) -> Recipe:
        """
        Обновляет рецепт.

        Args:
            instance (Recipe): Существующий рецепт.
            validated_data (dict): Проверенные данные.

        Returns:
            Recipe: Обновленный рецепт.
        """

        tags = validated_data.pop('tags', None)
        if tags is not None:
            instance.tags.set(tags)

        ingredients = validated_data.pop('ingredients', None)
        if ingredients is not None:
            instance.ingredients.clear()

            for ingredient in ingredients:
                amount = ingredient['amount']
                ingredient = get_object_or_404(Ingredient, pk=ingredient['id'])

                RecipeIngredients.objects.update_or_create(
                    recipe=instance,
                    ingredient=ingredient,
                    defaults={'amount': amount}
                )

        return super().update(instance, validated_data)

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

    class Meta:
        model = Recipe
        exclude = ('pub_date',)
