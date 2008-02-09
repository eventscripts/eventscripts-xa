import es
import os
import keyvalues
import playerlib
import xa

import psyco
psyco.full()

selfsettingfile = "%s/data/playerdata.txt" % es.getAddonPath('xa')
selfkeyvalues = keyvalues.KeyValues(name="playerdata.txt")
if os.path.exists(selfsettingfile):
    selfkeyvalues.load(selfsettingfile)

###########################
#Module methods start here#
###########################
class UserSetting(object):
    def __init__(self, module, pref):
        self.module = str(module)
        self.name = str(pref)
        if str(module) in xa.gModules:
            if not str(module) in selfkeyvalues:
                selfkeyvalues[str(module)] = keyvalues.KeyValues(name=str(module))
            if not str(pref) in selfkeyvalues[str(module)]:
                selfkeyvalues[str(module)][str(pref)] = keyvalues.KeyValues(name=str(pref))
        else:
            return None
    def __str__(self):
        return self.name
    def exists(self, userid):
        if es.exists("userid",userid):
            steamid = playerlib.uniqueid(userid, True)
            if steamid in selfkeyvalues[self.module][self.name]:
                return True
            else:
                return False
        else:
            return False
    def set(self, userid, value):
        if es.exists("userid",userid):
            steamid = playerlib.uniqueid(userid, True)
            selfkeyvalues[self.module][self.name][steamid] = value
            if selfkeyvalues[self.module][self.name][steamid] == value:
                return True
            else:
                return False
        else:
            return False
    def get(self, userid):
        if es.exists("userid",userid):
            steamid = playerlib.uniqueid(userid, True)
            if steamid in selfkeyvalues[self.module][self.name]:
                return selfkeyvalues[self.module][self.name][steamid]
            else:
                return None
        else:
            return False
            
def createUserSetting(module, pref):
    return UserSetting(module, pref)
    
def getUserSetting(module, pref):
    return createUserSetting(module, pref)

def saveKeyValues():
    selfkeyvalues.save(selfsettingfile)
