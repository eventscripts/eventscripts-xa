"""
Register groupauth models with the admin panel
"""
from models import Power, Player, Config, Group, PlayerRelation
from django.contrib import admin

register = admin.site.register

register(Power)
register(Player)
register(Config)
register(Group)
register(PlayerRelation)
