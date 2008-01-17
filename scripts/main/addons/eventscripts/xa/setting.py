import es
import os
import keyvalues

import xa

import psyco
psyco.full()

selfaddondir = str(es.server_var["eventscripts_addondir"]).replace("\\", "/")
selfmoddir = str(es.server_var["eventscripts_gamedir"]).replace("\\", "/")

selfsettingfile = "%s/data/setting.txt" % es.getAddonPath('xa')
selfmoduleconfig = "%s/cfg/xamodules.cfg" % selfmoddir
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
        xa.gModules[str(module)].variables[variable]._def = defaultvalue
        xa.gModules[str(module)].variables[variable]._descr = description
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
            del xa.gModules[str(module)].variables[variable]
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
    
def getVariables(module=None):
    varlist = []
    if module:
        for variable in sorted(xa.gModules[str(module)].variables):
            varlist.append(xa.gModules[str(module)].variables[str(variable)])
    else:    
        for module in sorted(xa.gModules):
            for variable in sorted(xa.gModules[str(module)].variables):
                varlist.append(xa.gModules[str(module)].variables[str(variable)])
    return varlist
    
def addVariables(module=None):
    varlist = []
    if module:
        for variable in sorted(xa.gModules[str(module)].variables):
            varlist.append(xa.gModules[str(module)].variables[str(variable)])
    else:
        for module in sorted(xa.gModules):
            for variable in sorted(xa.gModules[str(module)].variables):
                varlist.append(xa.gModules[str(module)].variables[str(variable)])
    if not os.path.isfile(selfmoduleconfig):
        f = open(selfmoduleconfig, 'w+')
        f.write('// XA Module configuration\n')
        f.write('// \n')
    else:
        f = open(selfmoduleconfig, 'r')
        for line in f:
            line = line.strip('\n')
            line = line.strip('\r')
            if line[0:2] != '//' and line[0:1] != '#' and line != '':
                data = line.split(' ', 1)
                for var in varlist:
                    if var.getName() == data[0]:
                        varlist.remove(var)
        f.close()
        f = open(selfmoduleconfig, 'a')
    for var in varlist:
        name = var.getName().replace('_', '')
        if name.isalnum():
            if len(var._descr) > 0:
                f.write('// '+str(var._descr)+'\n')
            if str(var).isdigit():
                f.write(str(var.getName())+' '+str(var)+'\n\n')
            else:
                f.write(str(var.getName())+' "'+str(var)+'"\n\n')
    f.close()

def saveVariables():
    varlist = []
    for module in sorted(xa.gModules):
        for variable in sorted(xa.gModules[str(module)].variables):
            varlist.append(xa.gModules[str(module)].variables[str(variable)])
    f = open(selfmoduleconfig, 'w+')
    f.write('// XA Module configuration\n')
    f.write('// \n')
    for var in varlist:
        name = var.getName().replace('_', '')
        if name.isalnum():
            if len(var._descr) > 0:
                f.write('// '+str(var._descr)+'\n')
            if str(var).isdigit():
                f.write(str(var.getName())+' '+str(var)+'\n\n')
            else:
                f.write(str(var.getName())+' "'+str(var)+'"\n\n')
    f.close()

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
