from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(verbose_name='Название ингридиента', max_length=100, unique=True)
    measurement_unit = models.CharField(verbose_name='Единица измерения', max_length=20)

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(verbose_name='Название тега', max_length=100, unique=True)
    slug = models.SlugField(verbose_name='Slug тега', unique=True)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
    
    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipes', verbose_name='Автор рецепта')
    name = models.CharField(verbose_name='Название рецепта', max_length=200)
    picture = models.ImageField(verbose_name='Изображение', upload_to='recipes/')
    description = models.TextField(verbose_name='Описание рецепта')
    ingredients = models.ManyToManyField(Ingredient, through='RecipeIngredient')
    tags = models.ManyToManyField(Tag)
    cooking_time = models.PositiveIntegerField(verbose_name='Время приготовления')
    pub_date = models.DateTimeField(verbose_name='Дата публикации', auto_now_add=True)

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, verbose_name='Рецепт')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, verbose_name='Ингридиент')
    amount = models.PositiveIntegerField(verbose_name='Количество ингридиента')

    class Meta:
        verbose_name = 'Ингридиенты в рецепте'
        verbose_name_plural = 'Ингридиенты в рецептах'
    
    def __str__(self):
        return (self.recipe, self.ingredient, self.amount, self.ingredient.measurement_unit)
