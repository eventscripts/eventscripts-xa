import es
import os
import popuplib
import playerlib
import langlib
import services
from xa.modules.xasettings import xasettings
from xa import xa

playerlimit = {}

#plugin information
info = es.AddonInfo()
info.name           = "Sounds"
info.version        = "0.1"
info.author         = "Hunter"
info.url            = "http://www.eventscripts.com/"
info.description    = "Clone of Mani Sounds feature for XA"
info.tags           = "admin quake sounds XA"

xasounds                            = xa.register('xasounds')
xalanguage                          = xasounds.language.getLanguage()
xaplayerdata_sounds                 = xasounds.playerdata.createUserSetting('sounds')

if xa.isManiMode():
    xasoundslist                    = xasounds.configparser.getAliasList('cfg/mani_admin_plugin/soundlist.txt', True)
else:
    xasoundslist                    = xasounds.configparser.getAliasList('soundlist.txt')

sounds_per_round                    = xasounds.setting.createVariable('sounds_per_round', '0', 'Number of sounds a regulary player can play in the course of a round')
sounds_filter_if_dead               = xasounds.setting.createVariable('sounds_filter_if_dead', '0', '1 = If a player is dead then only other dead players will hear it')
sounds_download                     = xasounds.setting.createVariable('sounds_auto_download', '0', '0 = Don\'t auto download files to client, 1 = automatically download files to client')
sounds_settings                     = xasounds.setting.createVariable('player_settings_sounds', '1', '0 = player settings default to off, 1 = player settings default to on')

def load():
    global mainmenu
    mainmenu = popuplib.easymenu('xamainsoundmenu',None,_mainmenu_select)
    mainmenu.settitle(xalanguage['sounds'])
    if xasoundslist:
        for sound in xasoundslist:
            for ll in langlib.getLanguages():
                mainmenu.addoption(str(sound), str(sound),1,langlib.getLangAbbreviation(ll))

    xasounds.registerCapability('play_adminsound', auth.ADMIN)
    xasounds.addMenu('xamainsoundmenu',xalanguage['sounds'],'xamainsoundmenu','play_sound','#all')
    xasettings.registerMethod(xasounds, _switch_setting, xalanguage["sounds"])

def unload():
    xa.unregister(xasounds)

def es_map_start(event_var):
    for userid in es.getUseridList():
        playerlimit[userid] = 0
    if xasoundslist:
        if int(sounds_download) == 1:
            for sound in xasoundslist:
                soundfile = str(xasoundslist[sound])
                es.stringtable('downloadables', 'sound/'+sound)

def round_start(event_var):
    for userid in es.getUseridList():
        playerlimit[userid] = 0

def player_activate(event_var):
    userid = int(event_var['userid'])
    playerlimit[userid] = 0
    if not xaplayerdata_sounds.exists(userid):
        xaplayerdata_sounds.set(userid, int(sounds_settings))
    
def player_disconnect(event_var):
    userid = int(event_var['userid'])
    playerlimit[userid] = 0

def player_spawn(event_var):
    userid = int(event_var['userid'])
    if not xaplayerdata_sounds.exists(userid):
        xaplayerdata_sounds.set(userid, int(sounds_settings))
            
def _switch_setting(userid):
    if int(xaplayerdata_sounds.get(userid)) == 1:
        xaplayerdata_sounds.set(userid, 0)
        player = playerlib.getPlayer(userid)
        es.tell(userid, xalanguage('turn off', {}, player.get("lang")))
    else:
        xaplayerdata_sounds.set(userid, 1)
        player = playerlib.getPlayer(userid)
        es.tell(userid, xalanguage('turn on', {}, player.get("lang")))

def _mainmenu_select(userid,choice,popupid):
    if choice in xasoundslist:
        _play_sound(xasoundslist[choice], choice, userid)

def _play_sound(soundfile, soundname, userid):
    auth = services.use("auth")
    if userid in playerlimit:
        playerlimit[userid] = playerlimit[userid] + 1
    else:
        playerlimit[userid] = 1
    if (playerlimit[userid] < int(sounds_per_round)) or (auth.isUseridAuthorized(userid, "play_adminsound") == True):
        player = playerlib.getPlayer(userid)
        if (int(sounds_filter_if_dead) == 1) and int(player.get('isdead')) == 1:
            useridlist_sound = playerlib.getUseridList('#dead')
        else:
            useridlist_sound = es.getUseridList()
        langdata = {"username":es.getplayername(userid),"sound":str(soundname)}
        for userid in useridlist_sound:
            if int(xaplayerdata_sounds.get(userid)) == 1:
                es.playsound(userid, soundfile, 1.0)
        for userid in useridlist_sound:
            if int(xaplayerdata_sounds.get(userid)) == 1:
                player = playerlib.getPlayer(userid)
                soundtext = xalanguage('played sound', langdata, player.get("lang"))
                es.tell(userid, soundtext)
    else:
        soundtext = xalanguage('sound limit', {}, player.get("lang"))
        es.tell(userid, soundtext)
