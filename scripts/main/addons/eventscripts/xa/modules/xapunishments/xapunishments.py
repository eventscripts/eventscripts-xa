import es
import xa
import xa.language
import xa.setting
import xa.playerdata
import xa.mani
import xa.maniconfig
import popuplib
from xa import xa

#plugin information
info = es.AddonInfo()
info.name = "XA:Punishments"
info.version = "0.1"
info.author = "Hunter"
info.url = "http://forums.mattie.info"
info.description = "Clone of Mani Player Punishments feature for XA"
info.tags = "admin punishments players"


def load():
    #Load Function for Player Settings for XA.
    xapunishments = xa.register('xapunishments')

def unload():
    xa.unRegister('xapunishments')
