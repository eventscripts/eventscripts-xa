import es
import os
import keyvalues

import xa

import psyco
psyco.full()

selfaddondir = str(es.server_var["eventscripts_addondir"]).replace("\\", "/")
selfmoddir = str(es.server_var["eventscripts_gamedir"]).replace("\\", "/")

selfsettingfile = "%s/data/setting.txt" % es.getAddonPath('xa')
selfkeyvalues = keyvalues.KeyValues(name="setting.txt")
if os.path.exists(selfsettingfile):
    selfkeyvalues.load(selfsettingfile)

###########################
#Module methods start here#
###########################
def createVariable(module, variable, defaultvalue=0, description=""):
    if str(module) in xa.gModules:
        if es.exists("variable", "mani_"+variable):
            variable = "mani_"+variable
        else:
            variable = "xa_"+variable
        var = es.ServerVar(variable, defaultvalue, description) 
        xa.gModules[str(module)].variables[variable] = var
        return var
    else:
        return None
        
def deleteVariable(module, variable):
    if str(module) in xa.gModules:
        if es.exists("variable", "mani_"+variable):
            variable = "mani_"+variable
        else:
            variable = "xa_"+variable
        if variable in xa.gModules[str(module)].variables:
            xa.gModules[str(module)].variables.remove(variable)
            var = es.ServerVar(variable, defaultvalue, description) 
            var.set(0)
    return None

def getVariable(module, variable):
    if str(module) in xa.gModules:
        if es.exists("variable", "mani_"+variable):
            variable = "mani_"+variable
        else:
            variable = "xa_"+variable
        if variable in xa.gModules[str(module)].variables:
            return xa.gModules[str(module)].variables[variable]
        else:
            return None
    else:
        return None

def getVariableName(variable):
    if es.exists("variable", "mani_"+variable):
        variable = "mani_"+variable
    else:
        variable = "xa_"+variable
    return variable

def createKeyValues(module):
    return useKeyValues(module)
    
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
