import es
import os
import keyvalues

import psyco
psyco.full()

selfaddondir = str(es.server_var["eventscripts_addondir"]).replace("\\", "/")
selfmoddir = str(selfaddondir).rsplit("/", 2)[0] + '/'

selfsettingfile = "%s/setting.txt" % es.getAddonPath('xa')
selfkeyvalues = keyvalues.KeyValues(name="setting.txt")
if os.path.exists(selfsettingfile):
    selfkeyvalues.load(selfsettingfile)

###########################
#Module methods start here#
###########################
def use(module):
    if module in selfkeyvalues:
        return selfkeyvalues[module]
    else:
        selfkeyvalues[module] = keyvalues.KeyValues(name=module)
        return selfkeyvalues[module]

def save():
    selfkeyvalues.save(selfsettingfile)
