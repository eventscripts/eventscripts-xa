from xa.groupauth.models import PlayerRelation, Power
from django import template
from django.utils.simplejson import dumps
from django.db.models import Q

register = template.Library()

@register.filter
def get_name(player, user):
    return PlayerRelation.objects.get(player=player, user=user).name

@register.filter
def get_groups(player, config):
    return player.groups.filter(config=config)

@register.filter
def get_powers(config):
    return Power.objects.filter(groups__config=config).distinct()

@register.filter
def js_get_powers(user):
    return dumps(map(lambda x: x[0], Power.objects.filter(Q(custom=False) | Q(custom=True, users=user)).distinct().values_list('name')))

@register.filter
def js_get_players(user):
    return dumps(map(lambda x: (x.steamid, get_name(x, user)), user.known_players.all()))

@register.filter
def js_get_groups(config):
    def get_flags(group):
        return map(lambda x: x[0], group.powers.all().values_list('name'))
    def get_players(group):
        return map(lambda x: x[0], group.players.all().values_list('steamid'))
    return dumps(map(lambda x: (x.name, get_flags(x), get_players(x)), config.groups.all()))