import es
import xa
import xa.language
import xa.setting
import xa.playerdata
import xa.manilib
import popuplib
from xa import xa

#plugin information
info = es.AddonInfo()
info.name = "XA:Settings"
info.version = "0.1"
info.author = "Hunter"
info.url = "http://forums.mattie.info"
info.description = "Clone of Mani Player Settings feature for XA"
info.tags = "admin settings players"


def load():
    #Load Function for Player Settings for XA.
    xasettings = xa.register('xasettings')

def unload():
    xa.unRegister('xasettings')
