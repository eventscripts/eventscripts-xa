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
    xasettingmenu.settitle(xalanguage["player settings"])
    xasettings.addMenu("xasettingmenu", xalanguage["player settings"], "xasettingmenu", "change_playersetting", "#all")

def unload():
    popuplib.delete("xasettingmenu")
    xa.unRegister(xasettings)

def _select_setting(userid, choice, name):
    pass
    
class Setting_switch(object):
    def __init__(self, setting, options, texts):
        self.name = setting
        self.texts = texts
        self.options = options
    def use(self, userid):
        pass

class Setting_menu(object):
    def __init__(self, setting, menu, texts):
        self.name = setting
        self.texts = texts
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
    def use(self, userid):
        pass
        
def registerSetting(setting, options, texts):
    pass
        
def registerSubmenu(setting, menu, texts):
    pass
