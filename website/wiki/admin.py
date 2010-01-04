from models import Category, Page, Content
from django.contrib import admin

register = admin.site.register

class ContentAdmin(admin.ModelAdmin):
    list_display = ['page', 'postdate', 'language']
    list_filter = ['page', 'language']

register(Category)
register(Page)
register(Content, ContentAdmin)
