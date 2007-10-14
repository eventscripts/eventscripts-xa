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
info.name           = "XA:Settings"
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
    xasettingmenu.cachemode = "user"
    xasettingmenu.settitle(xalanguage["player settings"])
    xasettings.addMenu("xasettingmenu", xalanguage["player settings"], "xasettingmenu", "change_playersetting", "#all")
    xasettings.addCommand("settings", _send_menu, "change_playersetting", "#all")

def unload():
    popuplib.delete("xasettingmenu")
    xa.unRegister(xasettings)
    
def _send_menu(userid, command, args, type):
    for setting in setting_object:
        setting_object[setting].rebuild(userid)
    xasettingmenu.recache([userid])
    xasettingmenu.send(userid)

def _select_setting(userid, choice, name):
    if choice in setting_object:
        setting_object[choice].use(userid, name)
    
class Setting_switch(object):
    def __init__(self, setting, options, texts):
        self.name = str(setting)
        self.texts = dict(texts)
        self.options = dict(options)
        xa.setting.createUserSetting(xasettings,self.name)
        xasettingmenu = popuplib.find("xasettingmenu")
        xasettingmenu.addoption(self.name, "Switch: "+self.name)
    def use(self, userid, popup):
        usersetting = xa.setting.getUserSetting(xasettings,self.name)
        useroption = usersetting.get(userid)
        nextoption = False
        for option in self.options:
            if nextoption == True:
                usersetting.set(userid, option)
                nextoption = False
            if self.options[option] == useroption:
                nextoption = True
        if nextoption == True:
            usersetting.set(userid, self.options[0])
        popuplib.send(popup, userid)
    def rebuild(self, userid):
        usersetting = xa.setting.getUserSetting(xasettings,self.name)
        useroption = usersetting.get(userid)
        for option in self.options:
            if self.options[option] == useroption:
                xasettingmenu.addoption(self.name, self.texts[option])

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
        
def registerSetting(setting, options, texts):
    if not setting in setting_object:
        setting_object[setting] = Setting_switch(setting, options, texts)
        
def registerSubmenu(setting, menu, texts):
    if not setting in setting_object:
        setting_object[setting] = Setting_menu(setting, menu, texts)

def registerMethod(setting, method, texts):
    if not setting in setting_object:
        setting_object[setting] = Setting_method(setting, method, texts)
