import es
import os
import keyvalues

import xa

import psyco
psyco.full()

selfaddondir = str(es.server_var["eventscripts_addondir"]).replace("\\", "/")
selfmoddir = str(selfaddondir).rsplit("/", 2)[0] + '/'

selfsettingfile = "%s/data/setting.txt" % es.getAddonPath('xa')
selfkeyvalues = keyvalues.KeyValues(name="setting.txt")
if os.path.exists(selfsettingfile):
    selfkeyvalues.load(selfsettingfile)

###########################
#Module methods start here#
###########################
def createVariable(module, variable, defaultvalue=0, description=""):
    if (xa.gManiMode == True) and ("xa_" != variable[0:3]):
        manivar = es.ServerVar("mani_"+variable, defaultvalue, description)
        if str(module) in xa.gModules:
            xa.gModules[str(module)].variablesMani[variable] = manivar
    if "xa_" == variable[0:3]:
        var = es.ServerVar(variable, defaultvalue, description)
    else:
        var = es.ServerVar("xa_"+variable, defaultvalue, description)
    if str(module) in xa.gModules:
        xa.gModules[str(module)].variables[variable] = var
    return var

def getVariable(module, variable):
    if str(module) in xa.gModules:
        if (xa.gManiMode == True) and ("xa_" != variable[0:3]) and (variable in xa.gModules[str(module)].variablesMani):
            return xa.gModules[str(module)].variablesMani[variable]
        elif variable in xa.gModules[str(module)].variables:
            return xa.gModules[str(module)].variables[variable]
        else:
            return None
    else:
        return None
    
def useKeyValues(module):
    if str(module) in xa.gModules:
        if str(module) in selfkeyvalues:
            return selfkeyvalues[str(module)]
        else:
            selfkeyvalues[str(module)] = keyvalues.KeyValues(name=str(module))
            return selfkeyvalues[str(module)]
    else:
        return None

def saveKeyValues():
    selfkeyvalues.save(selfsettingfile)
