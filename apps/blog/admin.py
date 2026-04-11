# Django modules
from django.contrib import admin

# Project modules
from .models import Category, Tag, Post, Comment


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name_en', 'slug']
    prepopulated_fields = {'slug': ('name_en',)}


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'author', 'category', 'status', 'created_at']
    list_filter = ['status', 'category', 'author']
    search_fields = ['title', 'body']
    prepopulated_fields = {'slug': ('title',)}
    autocomplete_fields = ['author'] # Makes finding users easier if many users
    filter_horizontal = ['tags'] # Better UI for ManyToMany fields


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'post', 'author', 'created_at']
    list_filter = ['created_at']