from models import *
from django.contrib import admin

r = admin.site.register

class ContentAdmin(admin.ModelAdmin):
    list_display = ['page', 'postdate', 'language']
    list_filter = ['page', 'language']

r(Category)
r(Page)
r(Content, ContentAdmin)
