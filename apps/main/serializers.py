from rest_framework import serializers
from slugify import slugify
from .models import Category, Post

class CategorySerializer(serializers.ModelSerializer):
    posts_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'created_at', 'posts_count']
        read_only_fields = ['id', 'slug', 'created_at', 'posts_count']

    def get_posts_count(self, obj):
        return obj.posts.filter(status='published').count()

    def create(self, validated_data):
        validated_data['slug'] = slugify(validated_data['name'], allow_unicode=True)
        return super().create(validated_data)


class PostListSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField()
    category = serializers.StringRelatedField()
    comments_count = serializers.ReadOnlyField()
    

    class Meta:
        model = Post
        fields = ['id', 'title', 'slug', 'content', 'image', 'category', 'author', 'status', 'created_at', 'updated_at', 'views_count', 'comments_count']
        read_only_fields = ['slug', 'author', 'created_at', 'updated_at', 'views_count']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if len(data['content']) > 200:
            data['content'] = data['content'][:200] + '...'
        return data


class PostDetailSerializer(serializers.ModelSerializer):
    """Сериализатор для детального просмотра поста"""

    author_info = serializers.SerializerMethodField()
    category_info = serializers.SerializerMethodField()
    comments_count = serializers.ReadOnlyField()

    class Meta:
        model = Post
        fields = [
            'id', 'title', 'slug', 'content', 'image', 'category',
            'category_info', 'author', 'author_info', 'status',
            'created_at', 'updated_at', 'views_count', 'comments_count'
        ]
        read_only_fields = ['slug', 'author', 'views_count']

    def get_author_info(self, obj):
        """Возвращает информацию об авторе поста"""
        return {
            'id': obj.author.id,
            'username': obj.author.username,
            'full_name': obj.author.full_name,
            'avatar': obj.author.avatar.url if obj.author.avatar else None,
        }

    def get_category_info(self, obj):
        """Возвращает информацию о категории поста"""

        if obj.category:
            return {
                'id': obj.category.id,
                'name': obj.category.name,
                'slug': obj.category.slug,
            }
        return None


class PostCreateUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и обновления постов"""

    class Meta:
        model = Post
        fields = ['title', 'content', 'image', 'category', 'status']

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        validated_data['slug'] = slugify(validated_data['title'], allow_unicode=True)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'title' in validated_data:
            validated_data['slug'] = slugify(validated_data['title'], allow_unicode=True)
        return super().update(instance, validated_data)


