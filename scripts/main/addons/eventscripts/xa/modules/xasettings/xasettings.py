import es
import xa
import xa.language
import xa.logging
import xa.setting
import xa.playerdata
import playerlib
import popuplib
from xa import xa

#plugin information
info = es.AddonInfo()
info.name           = "Settings"
info.version        = "0.1"
info.author         = "Hunter"
info.url            = "http://forums.mattie.info"
info.description    = "Clone of Mani Player Settings feature for XA"
info.tags           = "admin settings players"

setting_object = {}

xasettings                  = xa.register('xasettings')
xalanguage                  = xa.language.getLanguage(xasettings)

def load():
    #Load Function for Player Settings for XA.    
    xasettingmenu = popuplib.easymenu("xasettingmenu", "_tempcore", _select_setting)
    xasettingmenu.settitle(xalanguage["player settings"])
    xasettings.addMenu("xasettingmenu", xalanguage["player settings"], "xasettingmenu", "change_playersetting", "#all")
    xacommand = xasettings.addCommand("settings", _send_menu, "change_playersetting", "#all")
    xacommand.register(["console","say"])

def unload():
    popuplib.delete("xasettingmenu")
    xa.unRegister(xasettings)
    
def _send_menu():
    userid = es.getcmduserid()
    for setting in setting_object:
        setting_object[setting].rebuild(userid) # TODO: finish rebuild methods later
    xasettingmenu = popuplib.find("xasettingmenu")
    xasettingmenu.recache(userid)
    xasettingmenu.send(userid)

def _select_setting(userid, choice, name):
    if choice in setting_object:
        setting_object[choice].use(userid, name)

class Setting_menu(object):
    def __init__(self, setting, menu, texts):
        self.name = str(setting)
        self.texts = dict(texts)
        if popuplib.exists(menu):
            self.menu = menu
            self.menutype = "popup"
            self.menuobj = popuplib.find(self.menu)
        elif keymenulib.exists(menu):
            self.menu = menu
            self.menutype = "keymenu"
            self.menuobj = keymenulib.find(self.menu)
        elif settinglib.exists(menu):
            self.menu = menu
            self.menutype = "setting"
            self.menuobj = settinglib.find(self.menu)
        xasettingmenu = popuplib.find("xasettingmenu")
        xasettingmenu.addoption(setting, self.texts)
    def use(self, userid, popup):
        self.menu.send(userid)
    def rebuild(self, userid):
        pass
        
class Setting_method(object):
    def __init__(self, setting, method, texts):
        self.name = str(setting)
        self.texts = dict(texts)
        self.method = method
        xasettingmenu = popuplib.find("xasettingmenu")
        xasettingmenu.addoption(setting, self.texts)
    def use(self, userid, popup):
        if callable(self.method):
            self.method(userid)
        else:
            es.set("_xa_userid", str(userid))
            es.doblock(self.method)
    def rebuild(self, userid):
        pass
        
def registerSubmenu(setting, menu, texts):
    if not setting in setting_object:
        setting_object[setting] = Setting_menu(setting, menu, texts)

def registerMethod(setting, method, texts):
    if not setting in setting_object:
        setting_object[setting] = Setting_method(setting, method, texts)
