# Generated by Django 4.2.4 on 2023-08-24 13:07

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Favorite",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
            ],
            options={
                "verbose_name": "избранное",
                "verbose_name_plural": "Избранное",
            },
        ),
        migrations.CreateModel(
            name="Ingredient",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text="Введите название ингредиента",
                        max_length=200,
                        verbose_name="Название ингредиента",
                    ),
                ),
                (
                    "measurement_unit",
                    models.CharField(
                        help_text="Введите единицу измерения",
                        max_length=200,
                        verbose_name="Единица измерения",
                    ),
                ),
            ],
            options={
                "verbose_name": "Ингредиент",
                "verbose_name_plural": "Ингредиенты",
            },
        ),
        migrations.CreateModel(
            name="Recipe",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text="Введите название рецепта",
                        max_length=200,
                        verbose_name="Название рецепта",
                    ),
                ),
                (
                    "image",
                    models.ImageField(
                        blank=True,
                        help_text="Загрузите фото блюда",
                        upload_to="recipe/",
                        verbose_name="Картинка",
                    ),
                ),
                (
                    "text",
                    models.TextField(
                        help_text="Введите текстовое описание рецепта",
                        max_length=400,
                        verbose_name="Текстовое описание",
                    ),
                ),
                (
                    "cooking_time",
                    models.PositiveSmallIntegerField(
                        help_text="Введите время приготовления блюда по рецепту",
                        validators=[django.core.validators.MinValueValidator(0)],
                        verbose_name="Время приготовления",
                    ),
                ),
                (
                    "is_favorited",
                    models.BooleanField(
                        default=False,
                        help_text="Находится ли в избранном",
                        verbose_name="Находится ли в избранном",
                    ),
                ),
                (
                    "is_in_shopping_cart",
                    models.BooleanField(
                        default=False,
                        help_text="Находится ли в корзине",
                        verbose_name="Находится ли в корзине",
                    ),
                ),
                (
                    "pub_date",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Дата публикации"
                    ),
                ),
            ],
            options={
                "verbose_name": "Рецепт",
                "verbose_name_plural": "Рецепты",
                "ordering": ("-pub_date",),
            },
        ),
        migrations.CreateModel(
            name="RecipeIngredients",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "amount",
                    models.PositiveSmallIntegerField(
                        validators=[django.core.validators.MinValueValidator(1)],
                        verbose_name="Количество",
                    ),
                ),
            ],
            options={
                "verbose_name": "ингредиенты",
                "verbose_name_plural": "Ингредиенты",
            },
        ),
        migrations.CreateModel(
            name="Tag",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text="Введите название тэга",
                        max_length=95,
                        unique=True,
                        verbose_name="Название тэга",
                    ),
                ),
                (
                    "color",
                    models.CharField(
                        help_text="Введите цвет в формате HEX",
                        max_length=7,
                        unique=True,
                        verbose_name="Цвет",
                    ),
                ),
                (
                    "slug",
                    models.SlugField(
                        help_text="Введите читаемый URL для тега",
                        max_length=200,
                        unique=True,
                        verbose_name="Читаемый URL для тэга",
                    ),
                ),
            ],
            options={
                "verbose_name": "Тэг",
                "verbose_name_plural": "Тэги",
                "ordering": ["-id"],
            },
        ),
        migrations.CreateModel(
            name="ShoppingCart",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "recipe",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="in_shopping_list",
                        to="baseapp.recipe",
                        verbose_name="Рецепт",
                    ),
                ),
            ],
            options={
                "verbose_name": "список покупок",
                "verbose_name_plural": "Список покупок",
            },
        ),
    ]
