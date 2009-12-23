from models import Config, Group, Player, Power
from forms import EditForm
from xa.utils import render_to, response
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse

@login_required
@render_to
def overview(request):
    return 'groupauth/overview.htm', {}

@login_required
@render_to
def edit(request, config):
    if config:
        cfg = Config.objects.get_or_404(id=config, owner=request.user)
    else:
        cfg = None
    if request.method == 'POST':
        return save_edit(request, cfg)
    return 'groupauth/edit.htm', {'js_libraries': ['jquery', 'ui', 'gauth'], 'config': cfg}


def save_edit(request, cfg):
    form = EditForm(request.POST)
    if not form.is_valid():
        return HttpResponse(form.errors)
    data = form.clean()
    # Check cfgname
    if cfg is not None:
        if cfg.name != data['cfgname']:
            return HttpResponse('cfgname mismatch')
    else:
        cfg,_ = Config.objects.get_or_create(name=data['cfgname'], owner=request.user)
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
                     return HttpResponse('missing steamid alias for %s' % steamid)
                 aliases[steamid] = name
        # get flags 
        groupflags = request.POST.getlist('%s_flags' % group)
        if not groupflags:
            return HttpResponse('group needs flags, %s has none' % group)
        flags[group] = groupflags
    # everything went well, that's a surprise!
    # Now create the players
    _cache = {}
    for steamid,name in aliases.iteritems():
        if steamid in _cache:
            player = _cache[steamid]
        else:
            player,_ = Player.objects.get_or_create(steamid=steamid)
            _cache[steamid] = player
        if not request.user.known_players.filter(id=player.id):
            relation = PlayerRelation(player=player, user=request.user, name=name)
            relation.save()
    # And add the groups
    for name, steamids in realgroups.iteritems():
        g,_ = Group.objects.get_or_create(name=name, config=cfg)
        for steamid in steamids:
            g.players.add(_cache[steamid])
        # Add flags
        for flag in flags[name]:
            f = Power.objects.get_or_create(flag, request.user)
            g.powers.add(f)
    return HttpResponseRedirect(reverse('gauth:config', kwargs={'id': cfg.id}))

@login_required
@render_to
def config(request, id, msg=''):
    cfg = Config.objects.get_or_404(id=id, owner=request.user)
    return 'groupauth/config.htm', {'config': cfg}

@login_required
@response
def download(request, id):
    cfg = Config.objects.get_or_404(id=id)
    return cfg.render_plain(), 'plain/text'