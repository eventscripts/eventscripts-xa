import es
import xa
import xa.language
import xa.logging
import xa.setting
import playerlib
import popuplib
from xa import xa

#plugin information
info = es.AddonInfo()
info.name           = "Punishments"
info.version        = "0.1"
info.author         = "Hunter"
info.url            = "http://forums.mattie.info"
info.description    = "Clone of Mani Player Punishments feature for XA"
info.tags           = "admin punishments players"

punishment_choice = {}
punishment_method = {}
punishment_display = {}
punishment_target = {}
punishment_pmenus = {}

xapunishments               = xa.register('xapunishments')
xalanguage                  = xa.language.getLanguage(xapunishments)
xa_adminburn_anonymous      = xa.setting.createVariable(xapunishments, 'adminburn_anonymous', 0)
xa_adminslap_anonymous      = xa.setting.createVariable(xapunishments, 'adminslap_anonymous', 0)
xa_adminslay_anonymous      = xa.setting.createVariable(xapunishments, 'adminslay_anonymous', 0)
xa_admin_burn_time          = xa.setting.createVariable(xapunishments, 'admin_burn_time', 20)
xa_slap_to_damage           = xa.setting.createVariable(xapunishments, 'slap_to_damage', 10)

def load():
    #Load Function for Player Settings for XA.
    xapunishmentmenu = popuplib.easymenu("xapunishmentmenu", "_tempcore", _select_punishment)
    xapunishmentmenu.settitle(xalanguage["choose punishment"])
    xapunishments.addMenu("xapunishmentmenu", xalanguage["punish players"], "xapunishmentmenu", "punish_player", "#admin")
    
    xapunishtargetmenu = popuplib.easymenu("xapunishtargetmenu", "_tempcore", _select_target)
    xapunishtargetmenu.settitle(xalanguage["choose target"])
    xapunishtargetmenu.addoption("player", xalanguage["select a player"])
    xapunishtargetmenu.addoption("team3", xalanguage["counter terrorists"])
    xapunishtargetmenu.addoption("team2", xalanguage["terrorists"])
    xapunishtargetmenu.addoption("all", xalanguage["all players"])
    
    registerPunishment("burn", xalanguage["burn"], _punishment_burn)
    registerPunishment("slap", xalanguage["slap"], _punishment_slap)
    registerPunishment("slay", xalanguage["slay"], _punishment_slay)

def unload():
    for punishment in punishment_method:
        unRegisterPunishment(punishment)
    popuplib.delete("xapunishmentmenu")
    popuplib.delete("xapunishtargetmenu")
    for page in punishment_pmenus:
        page.delete()
    xa.unRegister(xapunishments)
    
def _select_punishment(userid, choice, name):
    punishment_choice[userid] = choice
    if not userid in punishment_target:
        popuplib.send("xapunishtargetmenu", userid)
    else:
        _punish_player(punishment_target[userid], punishment_choice[userid], userid)
        del punishment_target[userid]
    
def _select_target(userid, choice, name):
    if choice == "player":
        if userid in punishment_pmenus:
            punishment_pmenus[userid].delete()
        punishment_pmenus[userid] = popuplib.construct("xapunishplayermenu"+str(userid), "players", "#alive")
        punishment_pmenus[userid].settitle(xalanguage["choose player"])
        punishment_pmenus[userid].menuselectfb = _select_player
        punishment_pmenus[userid].send(userid)
    else:
        if choice == "team3":
            playerlist = playerlib.getUseridList("#ct")
        elif choice == "team2":
            playerlist = playerlib.getUseridList("#t")
        elif choice == "all":
            playerlist = es.getUseridList()
        for player in playerlist:
            _punish_player(player, punishment_choice[userid], userid)
            
def _select_player(userid, choice, name):
    _punish_player(choice, punishment_choice[userid], userid)

def _punish_player(userid, punishment, adminid):
    if callable(punishment_method[punishment]):
        xa.logging.log('xapunishments', "Admin "+str(adminid)+ " used punishment "+str(punishment)+" on player "+str(userid))
        punishment_method[punishment](userid, adminid)
    else:
        es.dbgmsg(0, "xapunishments.py: Cannot find method '"+str(punishment_method[punishment])+"'!")

def registerPunishment(punishment, name, method):
    if not punishment in punishment_method:
        punishment_method[punishment] = method
        punishment_display[punishment] = name
        xapunishmentmenu = popuplib.find("xapunishmentmenu")
        xapunishmentmenu.addoption(punishment, name, 1)
        return True
    else:
        return False
    
def unRegisterPunishment(punishment):
    if punishment in punishment_method:
        xapunishmentmenu = popuplib.find("xapunishmentmenu")
        xapunishmentmenu.addoption(punishment, punishment_display[punishment], 0)
        punishment_method[punishment] = None
        del punishment_display[punishment]
        return True
    else:
        return False
        
def punishPlayer(punishment, userid, adminid):
    if punishment in punishment_method:
        _punish_player(userid, punishment, adminid)
        return True
    else:
        return False

def sendPunishmentMenu(userid, victimid):
    for user in list(userid):
        punishment_target[user] = victimid
        xapunishmentmenu.send(user)

# The default punishments that ship with the module
def _punishment_burn(userid, adminid):
    if str(xa_adminburn_anonymous) == '0':
        tokens = {}
        tokens['admin']   = es.getplayername(adminid)
        tokens['user']    = es.getplayername(userid)
        for user in playerlib.getPlayerList():
            es.tell(user, xalanguage("admin burn", tokens, user.get("lang")))
    # TODO: need to add burn time
    es.server.cmd("es_xfire "+str(userid)+" !self Ignite")

def _punishment_slap(userid, adminid):
    if str(xa_adminslap_anonymous) == '0':
        tokens = {}
        tokens['admin']   = es.getplayername(adminid)
        tokens['user']    = es.getplayername(userid)
        tokens['health']  = str(xa_slap_to_damage)
        for user in playerlib.getPlayerList():
            es.tell(int(user), xalanguage("admin slap", tokens, user.get("lang")))
    player = playerlib.getPlayer(userid)
    player.set("health", int(xa_slap_to_damage))

def _punishment_slay(userid, adminid):
    if str(xa_adminslay_anonymous) == '0':
        tokens = {}
        tokens['admin']   = es.getplayername(adminid)
        tokens['user']    = es.getplayername(userid)
        for user in playerlib.getPlayerList():
            es.tell(int(userid), xalanguage("admin slay", tokens, user.get("lang")))
    player = playerlib.getPlayer(userid)
    player.kill()
