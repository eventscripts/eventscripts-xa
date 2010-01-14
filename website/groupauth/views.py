from models import Config, Group, Player, Power, PlayerRelation
from forms import EditForm
from xa.utils import render_to, response
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from breadcrumbs.base import lib

@render_to
@login_required
def overview(request):
    """
    Show the overview groupauth page for a user
    """
    return 'groupauth/overview.htm', {}
lib.register(overview, _('Groupauth Editor'))

@render_to
@login_required
def edit(request, cfgid=None):
    """
    Edit (or save changes) a config
    """
    if cfgid:
        cfg = Config.objects.get_or_404(id=cfgid, owner=request.user)
    else:
        cfg = None
    if request.method == 'POST':
        return save_edit(request, cfg)
    return 'groupauth/edit.htm', {'js_libraries': ['jquery', 'ui', 'gauth'], 'config': cfg}

def get_edit_name(path, args, kwargs):
    return _('Edit') if not kwargs.get('cfgid', False) else None

lib.register(edit, get_edit_name)


def save_edit(request, cfg):
    """
    Save changes to a configuration
    """
    form = EditForm(request.POST)
    if not form.is_valid():
        return HttpResponse(form.errors)
    data = form.clean()
    # Check cfgname
    if cfg is not None:
        if cfg.name != data['cfgname']:
            return HttpResponse('cfgname mismatch')
    else:
        cfg, created = Config.objects.get_or_create(
            name=data['cfgname'], owner=request.user
        )
    # Check groups/aliases info
    groups = data['groups'].split(',')
    realgroups = {}
    aliases = {}
    flags = {}
    for group in groups:
        steamids = request.POST.get(group, None)
        if steamids is None:
            return HttpResponse('missing group information for %s' % group) 
        realgroups[group] = steamids.split(',')
        for steamid in realgroups[group]:
            if steamid not in aliases:
                name = request.POST.get(steamid.replace(':','_'), None)
                if name is None:
                    return HttpResponse(
                        'missing steamid alias for %s' % steamid
                    )
            aliases[steamid] = name
        # get flags 
        groupflags = request.POST.getlist('%s_flags' % group)
        if not groupflags:
            return HttpResponse('group needs flags, %s has none' % group)
        flags[group] = groupflags
    # everything went well, that's a surprise!
    # Now create the players
    _cache = {}
    for steamid, name in aliases.iteritems():
        if steamid in _cache:
            player = _cache[steamid]
        else:
            player, created = Player.objects.get_or_create(steamid=steamid)
            _cache[steamid] = player
        if not request.user.known_players.filter(id=player.id):
            relation = PlayerRelation(
                player=player, user=request.user, name=name
            )
            relation.save()
    # And add the groups
    for name, steamids in realgroups.iteritems():
        thegroup, created = Group.objects.get_or_create(name=name, config=cfg)
        for steamid in steamids:
            thegroup.players.add(_cache[steamid])
        # Add flags
        for flag in flags[name]:
            theflag = Power.objects.get_or_create(flag, request.user)
            thegroup.powers.add(theflag)
    return HttpResponseRedirect(reverse('gauth:config', kwargs={'id': cfg.id}))

@render_to
@login_required
def config(request, cfgid, msg=''):
    """
    Display a nicely formatted config
    """
    cfg = Config.objects.get_or_404(id=cfgid, owner=request.user)
    return 'groupauth/config.htm', {'config': cfg}

def get_config_name(path, args, kwargs):
    cfg = Config.objects.get(id=kwargs['cfgid'])
    return cfg.name

lib.register(config, get_config_name)

@login_required
@response
def download(request, cfgid):
    """
    Return the unformatted config
    """
    cfg = Config.objects.get_or_404(id=cfgid)
    return cfg.render_plain(), 'plain/text'
