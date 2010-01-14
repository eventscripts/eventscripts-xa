from models import Category, Page, Content
from django.contrib import admin

register = admin.site.register

def lock_pages(modeladmin, request, queryset):
    queryset.update(locked=True)
lock_pages.short_description = "Lock Pages"

def unlock_pages(modeladmin, request, queryset):
    queryset.update(locked=True)
unlock_pages.short_description = "Unlock Pages"

def add_guide(modeladmin, request, queryset):
    queryset.update(in_sidebar=True)
add_guide.short_description = "Add to guides section in sidebar menu"

def remove_guide(modeladmin, request, queryset):
    queryset.update(in_sidebar=False)
remove_guide.short_description = "Remove from guides section in sidebar menu"


class PageAdmin(admin.ModelAdmin):
    list_display = ['name', 'locked', 'in_sidebar']
    actions = [lock_pages, unlock_pages, add_guide, remove_guide]

class ContentAdmin(admin.ModelAdmin):
    list_display = ['page', 'postdate', 'language']
    list_filter = ['page', 'language']

register(Category)
register(Page, PageAdmin)
register(Content, ContentAdmin)
