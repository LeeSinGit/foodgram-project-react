from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.forms import ValidationError


User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Название ингредиента',
        help_text='Введите название ингредиента'
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Единица измерения',
        help_text='Введите единицу измерения'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self) -> str:
        return f'{self.name}'


class Tag(models.Model):
    name = models.CharField(
        max_length=95,
        unique=True,
        verbose_name='Название тэга',
        help_text='Введите название тэга'
    )
    color = models.CharField(
        max_length=7,
        unique=True,
        verbose_name='Цвет',
        help_text='Введите цвет в формате HEX'
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        blank=False,
        null=False,
        verbose_name='Читаемый URL для тэга',
        help_text='Введите читаемый URL для тега'
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
        ordering = ['-id']

    def __str__(self) -> str:
        return self.name

    def clean(self):
        if len(self.color) != 7 or not self.color.startswith('#'):
            raise ValidationError(
                'Недопустимый цветовой формат.'
                'Цвет должен быть в шестнадцатеричном формате (#RRGGBB).'
            )


class Recipe(models.Model):
    name = models.CharField(
        max_length=200,
        blank=False,
        null=False,
        verbose_name='Название рецепта',
        help_text='Введите название рецепта'
    )
    author = models.ForeignKey(
        User,
        related_name='recipes',
        blank=False,
        null=False,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        help_text='Введите автора рецепта'
    )
    image = models.ImageField(
        upload_to='recipe/',
        blank=True,
        verbose_name='Картинка',
        help_text='Загрузите фото блюда'
    )
    text = models.TextField(
        max_length=400,
        blank=False,
        null=False,
        verbose_name='Текстовое описание',
        help_text='Введите текстовое описание рецепта'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        blank=False,
        related_name='recipes',
        verbose_name='Ингредиенты',
        help_text='Введите список ингредиентов'
    )
    tags = models.ManyToManyField(
        Tag,
        blank=False,
        related_name='recipes',
        verbose_name='Тэги',
        help_text='Введите тэг/тэги'
    )
    cooking_time = models.PositiveSmallIntegerField(
        blank=False,
        null=False,
        validators=[MinValueValidator(0)],
        verbose_name='Время приготовления',
        help_text='Введите время приготовления блюда по рецепту'
    )
    is_favorited = models.BooleanField(
        blank=False,
        null=False,
        default=False,
        verbose_name='Находится ли в избранном',
        help_text='Находится ли в избранном'
    )
    is_in_shopping_cart = models.BooleanField(
        blank=False,
        null=False,
        default=False,
        verbose_name='Находится ли в корзине',
        help_text='Находится ли в корзине'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date', )

    def __str__(self) -> str:
        return f'{self.name}'

    def get_ingredient_count(self):
        return self.ingredients.count()


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='in_favorite',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'избранное'
        verbose_name_plural = 'Избранное'

        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_favorite_recipe'
            ),
        )

    def __str__(self):
        return f'Рецепт {self.recipe} в избранном у {self.user}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_list',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='in_shopping_list',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'список покупок'
        verbose_name_plural = 'Список покупок'

        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_shopping_list_recipe'
            ),
        )

    def __str__(self):
        return f'Рецепт {self.recipe} в списке покупок у {self.user}'


class RecipeIngredients(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.PROTECT,
        verbose_name='Ингредиент'
    )
    amount = models.PositiveSmallIntegerField(
        validators=(MinValueValidator(1),),
        verbose_name='Количество'
    )

    class Meta:
        verbose_name = 'ингредиенты'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'В рецепте {self.recipe} есть ингредиент {self.ingredient}'
