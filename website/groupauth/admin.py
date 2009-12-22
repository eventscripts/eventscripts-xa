from models import *
from django.contrib import admin

r = admin.site.register

r(Power)
r(Player)
r(Config)
r(Group)