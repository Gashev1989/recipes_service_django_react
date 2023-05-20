import base64
import webcolors

from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from recipes.models import FavoriteRecipe, Tag, Ingredient, Recipe, RecipeIngredient, ShoppingRecipe
from users.models import Follow, User


class UserSerializer(serializers.ModelSerializer):
    """Сериалайзер для пользователя."""
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
        )
        extra_kwargs = {'password': {'write_only': True}}
    
    def get_is_subscribed(self, obj):
        """Метод определения поля is_subscribed."""
        user = self.context.get("request").user
        if user.is_authenticated:
            return Follow.objects.filter(follower=user, following=obj).exists()
        return False
    
    def create(self, validated_data):
        """Метод создания нового пользователя."""
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class Hex2NameColor(serializers.Field):
    """Конвертор цвета в HEX-формат."""
    def to_representation(self, value):
        return value
    def to_internal_value(self, data):
        try:
            data = webcolors.hex_to_name(data)
        except ValueError:
            raise serializers.ValidationError('Для этого цвета нет имени')
        return data


class IngredientSerializer(serializers.ModelSerializer):
    """Сериалайзер для ингридиента."""
    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
        )


class TagSerializer(serializers.ModelSerializer):
    """Сериалайзер для тега."""
    color = Hex2NameColor()

    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug',
        )


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериалайзер для ингридиента в рецепте."""
    name = serializers.ReadOnlyField(
        source='ingredient.name'
    )
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'name',
            'amount',
            'measurement_unit',
        )


class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
    """Сериалайзер для создания ингридиента в рецепте."""
    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'amount',
        )


class RecipeSerializer(serializers.ModelSerializer):
    """Сериалайзер рецепта."""
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(many=False, read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_card = serializers.SerializerMethodField()
    image = Base64ImageField(required=True, allow_null=False)
    ingredients = RecipeIngredientSerializer(many=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_card',
            'name',
            'image',
            'text',
            'cooking_time',
            )
    
    def get_is_favorited(self, obj):
        user = self.context.get("request").user
        if user.is_authenticated:
            return FavoriteRecipe.objects.filter(user=user, recipe=obj).exists()
        return False
    
    def get_is_in_shopping_card(self, obj):
        user = self.context.get("request").user
        if user.is_authenticated:
            return ShoppingRecipe.objects.filter(user=user, recipe=obj).exists()
        return False


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    """Сериалайзер для создания и редактирования рецептов."""
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all())
    ingredients = RecipeIngredientCreateSerializer(many=True)
    author = UserSerializer(read_only=True, many=False)
    image = Base64ImageField(required=True, allow_null=False)
    
    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'ingredients',
            'author',
            'name',
            'text',
            'cooking_time',
            'image',
        )

    def create(self, validated_data):
        ingredients_list = validated_data.pop('ingredients')
        tag_list = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tag_list)
        RecipeIngredient.objects.bulk_create(
            [
                RecipeIngredient(
                    recipe=recipe,
                    ingredient=get_object_or_404(
                        Ingredient,
                        pk=ingredient.get('id')),
                    amount=ingredient.get('amount')
                )
                for ingredient in ingredients_list
            ]
        )
        return recipe
    
    def udpate(self, instance, validated_data):
        ingredients_list = validated_data.pop('ingredients')
        tag_list = validated_data.pop('tags')
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time)
        Tag.objects.filter(recipe=instance).delete()
        RecipeIngredient.objects.filter(recipe=instance).delete()
        instance.tags.set(tag_list)
        RecipeIngredient.objects.bulk_create(
            [
                RecipeIngredient(
                    recipe=instance,
                    ingredient=get_object_or_404(
                        Ingredient,
                        pk=ingredient.get('id')),
                    amount=ingredient.get('amount')
                )
                for ingredient in ingredients_list
            ]
        )
        instance.save()
        return instance
