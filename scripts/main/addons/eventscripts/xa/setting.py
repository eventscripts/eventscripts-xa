import es
import os
import time
import keyvalues
import xa

import psyco
psyco.full()

gSettingFile = "%s/data/setting.txt" % es.getAddonPath('xa')
gModuleConfig = "%s/cfg/xamodules.cfg" % xa.gGameDir
gKeyValues = keyvalues.KeyValues(name="setting.txt")
if os.path.exists(gSettingFile):
    gKeyValues.load(gSettingFile)

###########################
#Module methods start here#
########################################################
# All methods that should be able to be called through #
# the API need to have "module" as first parameter     #
########################################################
def createVariable(module, variable, defaultvalue=0, description=""):
    if str(module) in xa.gModules:
        x = xa.gModules[str(module)]
        if es.exists("variable", "mani_"+variable):
            variable = "mani_"+variable
        else:
            variable = "xa_"+variable
        x.variables[variable] = es.ServerVar(variable, defaultvalue, description)
        x.variables[variable]._def = defaultvalue
        x.variables[variable]._descr = description
        return x.variables[variable]
    else:
        return None
        
def deleteVariable(module, variable):
    if str(module) in xa.gModules:
        x = xa.gModules[str(module)]
        if es.exists("variable", "mani_"+variable):
            variable = "mani_"+variable
        else:
            variable = "xa_"+variable
        if variable in x.variables:
            del x.variables[variable]
            var = es.ServerVar(variable, defaultvalue, description) 
            var.set(0)
    return None

def getVariable(module, variable):
    if str(module) in xa.gModules:
        x = xa.gModules[str(module)]
        if es.exists("variable", "mani_"+variable):
            variable = "mani_"+variable
        else:
            variable = "xa_"+variable
        if variable in x.variables:
            return x.variables[variable]
        else:
            return None
    else:
        return None

###### parameter ordering to be backwards compatible ######
def getVariableName(variable = None, module = None):
    if module:
        variable = str(module) 
    if es.exists("variable", "mani_"+variable):
        variable = "mani_"+variable
    else:
        variable = "xa_"+variable
    return variable
    
def getVariables(module = None):
    varlist = []
    if str(module) in xa.gModules:
        x = xa.gModules[str(module)]
        for variable in sorted(x.variables):
            varlist.append(x.variables[variable])
    else:    
        for module in sorted(xa.gModules):
            x = xa.gModules[module]
            for variable in sorted(x.variables):
                varlist.append(x.variables[variable])
    return varlist
    
def addVariables(module = None):
    writeaddstamp = True
    varlist = getVariables(module)
    if not os.path.isfile(gModuleConfig):
        writeaddstamp = False
        f = open(gModuleConfig, 'w')
        f.write('// XA Module Configuration\n')
        f.write('// Written on '+time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())+'\n')
        f.write('// \n\n')
    else:
        f = open(gModuleConfig, 'rU')
        for line in f:
            line = line.strip('\n')
            line = line.strip('\r')
            if line[0:2] != '//' and line[0:1] != '#' and line != '':
                data = line.split(' ', 1)
                for var in varlist:
                    if var.getName() == data[0]:
                        varlist.remove(var)
        f.close()
        f = open(gModuleConfig, 'a')
    if writeaddstamp and varlist:
        f.write('// Added on '+time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())+'\n')
        f.write('// \n\n')
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

def saveVariables(module = None):
    varlist = getVariables()
    f = open(gModuleConfig, 'w')
    f.write('// XA Module Configuration\n')
    f.write('// Written on '+time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())+'\n')
    f.write('// \n\n')
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
        if str(module) in gKeyValues:
            return gKeyValues[str(module)]
        else:
            gKeyValues[str(module)] = keyvalues.KeyValues(name=str(module))
            return gKeyValues[str(module)]
    else:
        return None

def saveKeyValues(module = None):
    gKeyValues.save(gSettingFile)
