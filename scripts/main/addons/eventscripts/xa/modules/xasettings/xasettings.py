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

xasettings                  = xa.register('xasettings')
xalanguage                  = xa.language.getLanguage(xasettings)

def load():
    #Load Function for Player Settings for XA.
    xasettings = xa.find('xasettings')
    
    xasettingmenu = popuplib.easymenu("xasettingmenu", "_tempcore", _select_setting)
    xasettingmenu.settitle(xalanguage["player settings"])
    xapunishments.addMenu("xasettingmenu", xalanguage["player settings"], "xasettingmenu", "change_playersetting", "#all")

def unload():
    popuplib.delete("xasettingmenu")
    xa.unRegister('xasettings')

def _select_setting(userid, choice, name):
    pass
