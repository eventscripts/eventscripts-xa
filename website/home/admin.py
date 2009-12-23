from models import *
from django.contrib import admin

r = admin.site.register

r(News)
r(Release)
