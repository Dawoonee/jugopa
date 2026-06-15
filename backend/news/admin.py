from django.contrib import admin

from .models import Sector, NewsArticle, SectorCardNews


@admin.register(Sector)
class SectorAdmin(admin.ModelAdmin):
    list_display = ('name', 'display_order', 'is_active')
    list_editable = ('display_order', 'is_active')


@admin.register(NewsArticle)
class NewsArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'source', 'published_at')
    list_filter = ('source', 'sectors')
    search_fields = ('title',)


@admin.register(SectorCardNews)
class SectorCardNewsAdmin(admin.ModelAdmin):
    list_display = ('target_date', 'rank', 'sector', 'headline', 'article_count')
    list_filter = ('target_date', 'sector')
