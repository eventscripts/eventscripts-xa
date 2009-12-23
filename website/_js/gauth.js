var steamid_re = new RegExp(/STEAM_\d:\d:\d{1,20}/);
var group_re = new RegExp(/^[a-zA-Z0-9_-]+$/);
var draggable_options = {
    helper: 'clone',
    cursor: 'move',
    containment: 'document',
};

var eles = {
    hidden: $('#hiddendiv'),
    save: $('#save'),
    gerror: $('#group_error'),
    serror: $('#steamid_error'),
    npsid: $('#new_player_steamid'),
    npname: $('#new_player_name'),
    npbut: $('#new_player_button'),
    ngname: $('#new_group_name'),
    ngbut: $('#new_group_button'),
    player_adder: $('#player_adder'),
    gfield: $('#groups_field'),
    sfield: $('#steamids_field'),
    cfbut: $('#custom_flag_button'),
    cffield: $('#custom_flag_field'),
};

var groups = {
    lock: false,
    data: {},
    aliases: {},
    binds: {},
    id: 0,
    
    get_id: function()
    {
        this.id++;
        return 'generic_id_' + this.id;
    },
    
    bind: function (id, data)
    {
        this.binds[id] = data;
    },
    
    resolve: function (id)
    {
        return this.binds[id];
    },

    alias: function (steamid, name)
    {
        this.aliases[steamid] = name;
    },
    
    add: function (groupname, steamid)
    {
        if (groupname in this.data)
        {
            this.data[groupname].push(steamid);
        }
        else
        {
            this.data[groupname] = [steamid];
        }
    },
    
    remove: function (groupname, steamid)
    {
        this.data[groupname].splice(this.data[groupname].indexOf(steamid), 1);
    },
    
    delgroup: function (groupname)
    {
        delete this.data[groupname];
    },
    
    inin: function (groupname, steamid)
    {
        if (groupname in this.data)
        {
            if (this.data[groupname].indexOf(steamid) != -1)
            {
                return true;
            }
        }
        return false;
    },
    
    build_form: function ()
    {
         var gs = [];
         for (group in this.data)
         {
             gs.push(group);
             eles.hidden.append(this.mkinput(group, this.data[group].join(',')));
         }
         eles.gfield.val(gs.join(','));
         for (steamid in this.aliases)
         {
             name = this.aliases[steamid];
             eles.hidden.append(this.mkinput(steamid.replace(/:/g,'_'), name));
         }
    },
    
    mkinput: function (name, value)
    {
        return '<input type="hidden" name="' + name + '" value="' + value + '" />';
    },
};

function droppable_filter(item)
{
    return true;
}

function undrop_it()
{
    var ele = $(this);
    var obj = groups.resolve(ele.attr('id'));
    var steamid = obj[0];
    var group = obj[1];
    ele.parent().remove();
    groups.remove(group, steamid);
}

function drop_it (ev, ui)
{
    var verbose = ui.draggable.text();
    var steamid = ui.draggable.attr('id');
    var group = $(this).parent().attr('id');
    add_player_to_group(steamid, group, verbose);
}

function add_player_to_group (steamid, group, verbose)
{
    var nextid = groups.get_id();
    groups.add(group, steamid);
    groups.bind(nextid, [steamid, group]);
    $('#' + nextid).bind('click', undrop_it);
    $('#' + group + ' > .group').append('<li>' + verbose + '<input type="button" id="' + nextid + '" value="(remove)" /></li>');
}

var droppable_options = {
    accept: function (item) { return !groups.inin($(this).parent().attr('id'), item.attr('id')); },
    hoverClass: 'gauth-hover',
    drop: drop_it,
}

function draggable(obj)
{
    obj.draggable(draggable_options);
}

function droppable(obj)
{
    obj.droppable(droppable_options);
}

function add_player()
{
    var steamid = $('#new_player_steamid').val().toUpperCase();
    var name = $('#new_player_name').val();
    _add_player(steamid, name);
}

function _add_player(steamid, name)
{
    var obj = $('#' + steamid.replace(/:/g,'\\:'));
    if (obj.length)
    {
        return;
    }
    error = $('#steamid_error');
    if (!steamid_re.test(steamid))
    {
        if (error.hasClass('hidden'))
        {
            error.removeClass('hidden');
        }
        return;
    }
    if (!error.hasClass('hidden'))
    {
        error.addClass('hidden');
    }
    $('#player_adder').before('<li id="' + steamid + '">' + name + ' (' + steamid + ')</li>');
    draggable($('#' + steamid.replace(/:/g,'\\:')));
    groups.alias(steamid, name);
}

function remove_group()
{
    var ele = $(this);
    var id = ele.attr('id');
    var groupname = groups.resolve(id);
    groups.delgroup(groupname);
    $('#' + groupname).remove();
}

function add_group()
{
    var groupname = $('#new_group_name').val();
    _add_group(groupname);
}

function _add_group(groupname)
{
    var obj = $('#' + groupname);
    if (obj.length)
    {
        return;
    }
    error = $('#group_error');
    if (!group_re.test(groupname))
    {
        if (error.hasClass('hidden'))
        {
            error.removeClass('hidden');
        }
        return;
    }
    if (!error.hasClass('hidden'))
    {
        error.addClass('hidden');
    }
    var nextid = groups.get_id();
    var nextid2 = groups.get_id();
    $('#groups').append('<div class="groupwrapper" id="' + groupname + '"><h2>' + groupname + '</h2><input type="button" id="' + nextid + '" value="(remove)" /><ul class="group"></ul><div class="group_flags"></div></div>');
    groups.bind(nextid, groupname);
    $('#' + nextid).bind('click', remove_group);
    droppable($('.group'));
    var flags_div = $('#' + groupname + ' > ' + '.group_flags');
    for (i in gauth_flags)
    {
        var flag = gauth_flags[i];
        flags_div.append(flag + ': <input type="checkbox" name="' + groupname + '_flags" value="' + flag + '" />');
    }
}

function add_flag()
{
    var newflag = eles.cffield.val();
    if (!newflag)
    {
        return;
    }
    if (gauth_flags.indexOf(newflag) != -1)
    {
        return;
    }
    gauth_flags.push(newflag);
    $('.group_flags').each(function (i) {$(this).append(newflag + ': <input type="checkbox" value="' + newflag + '" name="' + $(this).parent().attr('id') + '_flags"/>');});
}

function save()
{
    groups.build_form();
    return true;
    if (!groups.lock)
    {
        groups.lock = true;
        groups.build_form();
        $("form").trigger('submit');
        return false
    }
    else
    {
        return true;
    }
}

function gauth_load()
{
    var _cache = {};
    for (i in gauth_players)
    {
        var steamid = gauth_players[i][0];
        var name = gauth_players[i][1];
        _add_player(steamid, name);
        _cache[steamid] = name;
    }
    for (i in gauth_groups)
    {
        var groupname = gauth_groups[i][0];
        var flags = gauth_groups[i][1];
        var players = gauth_groups[i][2];
        _add_group(groupname);
        for (i in flags)
        {
            var flag = flags[i];
            $("input[name='" + groupname + "_flags'][value='" + flag + "']").attr('checked', true);
        }
        for (i in players)
        {
            var steamid = players[i];
            var verbose = _cache[steamid] + ' (' + steamid + ')';
            add_player_to_group(steamid, groupname, verbose);
        }
    }
    eles.npbut.bind('click', add_player);
    eles.ngbut.bind('click', add_group);
    eles.cfbut.bind('click', add_flag);
    $("form").submit(save);
}