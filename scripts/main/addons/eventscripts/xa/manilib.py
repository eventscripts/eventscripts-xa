import es
import os
import keyvalues

import xa

import psyco
psyco.full()

selfaddondir = str(es.server_var["eventscripts_addondir"]).replace("\\", "/")
selfmoddir = str(selfaddondir).rsplit("/", 2)[0] + '/'

###########################
#Module methods start here#
###########################
def loadModules():
    filename = "%s/%s" % (es.getAddonPath('xa'), 'static/mani.txt')
    if os.path.exists(filename):
        f = open(filename, "r")
        try:
            for line in f:
                linelist = line.strip().split("|", 3)
                variable = es.ServerVar(str(linelist[0]), 0)
                if str(linelist[2]) == str(variable):
                    if not es.exists("script", "xa/modules/"+linelist[2]):
                        es.load("xa/modules/"+str(linelist[1]))
                elif str(linelist[3]) != str(variable):
                    if not es.exists("script", "xa/modules/"+linelist[2]):
                        es.load("xa/modules/"+str(linelist[1]))
        finally:
            f.close()
    else:
        raise FileError("Could not find xa/static/mani.txt!")
        
def loadVariableList():
    filename = "%s/%s" % (es.getAddonPath('xa'), 'static/maniconfig.txt')
    if os.path.exists(filename):
        f = open(filename, "r")
        try:
            for line in f:
                linelist = line.strip().split("|", 2)
                es.ServerVar(str(linelist[0]), str(linelist[1]), str(linelist[2]))
        finally:
            f.close()
        return True
    else:
        raise FileError("Could not find xa/static/maniconfig.txt!")

def getList(filename):
    filename = "%s/%s" % (selfmoddir, filename)
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

def getAliasList(filename):
    filename = "%s/%s" % (selfmoddir, filename)
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
            
def getKeyList(filename):
    filename = "%s/%s" % (selfmoddir, filename)
    if os.path.exists(filename):
        kv = keyvalues.KeyValues(name=basename(filename))
        kv.load(filename)
        return kv
    else:
        return False
            
def getVariableList():
    filename = "%s/%s" % (es.getAddonPath('xa'), 'static/maniconfig.txt')
    if os.path.exists(filename):
        lines = {}
        f = open(filename, "r")
        try:
            for line in f:
                linelist = line.strip().split("|", 2)
                lines[linelist[0]] = es.ServerVar(str(linelist[0]), str(linelist[1]), str(linelist[2]))
        finally:
            f.close()
        return lines
    else:
        raise FileError("Could not find xa/static/maniconfig.txt!")

def getVariable(variable):
    filename = "%s/%s" % (es.getAddonPath('xa'), 'static/maniconfig.txt')
    if os.path.exists(filename):
        lines = {}
        f = open(filename, "r")
        try:
            for line in f:
                linelist = line.strip().split("|", 2)
                if linelist[0] == str(variable):
                    return es.ServerVar(str(linelist[0]), str(linelist[1]), str(linelist[2]))
        finally:
            f.close()
        return None
    else:
        raise FileError("Could not find xa/static/maniconfig.txt!")

def getVariableName(variable):
    if xa.isManiMode:
        if not "mani_" == variable[0:5]:
            variable = "mani_"+variable
    else:
        if not "xa_" == variable[0:3]:
            variable = "xa_"+variable
    return variable
