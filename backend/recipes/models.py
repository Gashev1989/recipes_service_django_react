from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

MINIMAL_VALUE = 1

User = get_user_model()


class Ingredient(models.Model):
    """Модель ингредиента."""
    name = models.CharField(
        verbose_name='Название ингредиента',
        max_length=100,
        blank=False
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=20,
        blank=False
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_name_measurement_unit')]
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Tag(models.Model):
    """Модель тега."""
    name = models.CharField(
        verbose_name='Название тега',
        max_length=100,
        unique=True
    )
    slug = models.SlugField(
        verbose_name='Slug тега',
        unique=True
    )
    color = models.CharField(
        verbose_name='Цветовой HEX-код тега',
        max_length=7,
        unique=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'slug', 'color'],
                name='unique_name_slug_color')]
        ordering = ('name',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецепта."""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта'
    )
    name = models.CharField(
        verbose_name='Название рецепта',
        max_length=200
    )
    image = models.ImageField(
        verbose_name='Изображение',
        upload_to='recipes/'
    )
    text = models.TextField(
        verbose_name='Описание рецепта'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='Component',
        verbose_name='Ингредиенты',
        related_name='recipes'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
        related_name='recipes'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления в минутах',
        validators=[MinValueValidator(MINIMAL_VALUE)]
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class Component(models.Model):
    """Модель для определения количества ингредиента в рецепте."""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='components'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
        related_name='components'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество ингредиента',
        validators=[MinValueValidator(MINIMAL_VALUE)]
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['ingredient', 'recipe'],
                name='unique_component')]
        ordering = ('recipe',)
        verbose_name = 'Ингредиенты в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'

    def __str__(self):
        return (f'{self.recipe.name}: '
                f'{self.ingredient.name} - '
                f'{self.amount} '
                f'{self.ingredient.measurement_unit}')


class FavoriteRecipe(models.Model):
    """Модель рецепта в избранном."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_favorite_recipe')]
        ordering = ('user',)
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'

    def __str__(self):
        return f'{self.recipe.name} - {self.user}'


class ShoppingCart(models.Model):
    """Модель рецепта в корзине покупок."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shop_cart'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shop_cart'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_shop_recipe')]
        ordering = ('user',)
        verbose_name = 'Рецепт в корзине'
        verbose_name_plural = 'Рецепты в корзине'

    def __str__(self):
        return f'{self.recipe.name} - {self.user}'
