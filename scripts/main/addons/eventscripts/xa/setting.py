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
def getList(module, filename):
    if str(module) in xa.gModules:
        filename = "%s/modules/%s/%s" % (es.getAddonPath('xa'), str(module), filename)
        if os.path.exists(filename):
            lines = []
            f = os.open(filename, "r")
            try:
                for line in f:
                    lines[len(lines)+1] = line
            finally:
                f.close()
            return lines
        else:
            return False
    else:
        return False

def getAliasList(module, filename):
    if str(module) in xa.gModules:
        filename = "%s/modules/%s/%s" % (es.getAddonPath('xa'), str(module), filename)
        if os.path.exists(filename):
            lines = {}
            f = open(filename, "r")
            try:
                for line in f:
                    linelist = line.split(" ", 1)
                    lines[linelist[0]] = linelist[1]
            finally:
                f.close()
            return lines
        else:
            return False
    else:
        return False
            
def getKeyList(module, filename):
    if str(module) in xa.gModules:
        filename = "%s/modules/%s/%s" % (es.getAddonPath('xa'), str(module), filename)
        if os.path.exists(filename):
            kv = keyvalues.KeyValues(name=basename(filename))
            kv.load(filename)
            return kv
        else:
            return False
    else:
        return False

def createVariable(module, variable, defaultvalue=0, description=""):
    if str(module) in xa.gModules:
        if not "xa_" == variable[0:3]:
            variable = "xa_"+variable
        var = es.ServerVar(variable, defaultvalue, description) 
        xa.gModules[str(module)].variables[variable] = var
        return var
    else:
        return None

def getVariable(module, variable):
    if str(module) in xa.gModules:
        if not "xa_" == variable[0:3]:
            variable = "xa_"+variable
        if variable in xa.gModules[str(module)].variables:
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
