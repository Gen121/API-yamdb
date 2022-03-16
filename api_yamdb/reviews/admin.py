from django.contrib import admin

from .models import Category, Genre, Title, User


admin.site.register(User)


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'year',
        'rating',
        'description',
        'category',
    )
    search_fields = ('name', 'description')
    list_filter = ('rating', 'year')
    empty_value_display = '-пусто-'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'slug',
    )


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'slug',
    )
