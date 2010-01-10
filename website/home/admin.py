"""
Register news and releases with the admin panel, no customization
"""
from models import News, Release, StaticPage, Translation
from django.contrib import admin

register = admin.site.register

class NewsAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}

class ReleaseAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("version",)}

class TranslationAdmin(admin.ModelAdmin):
    list_display = ('title', 'lang_code', 'staticpage')

register(News, NewsAdmin)
register(Release, ReleaseAdmin)
register(StaticPage)
register(Translation, TranslationAdmin)
