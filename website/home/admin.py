"""
Register news and releases with the admin panel, no customization
"""
from models import News, Release
from django.contrib import admin

register = admin.site.register

register(News)
register(Release)
