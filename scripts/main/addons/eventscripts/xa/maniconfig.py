import es
import os
import keyvalues

import psyco
psyco.full()

selfaddondir = str(es.server_var["eventscripts_addondir"]).replace("\\", "/")
selfmoddir = str(selfaddondir).rsplit("/", 2)[0] + '/'

###########################
#Module methods start here#
###########################
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
    filename = "%s/%s" % (es.getAddonPath('xa'), 'data/maniconfig.txt')
    if os.path.exists(filename):
        lines = {}
        f = open(filename, "r")
        try:
            for line in f:
                linelist = line.split("|", 2)
                lines[linelist[0]] = es.ServerVar(linelist[0], linelist[1], linelist[2])
        finally:
            f.close()
        return lines
    else:
        raise FileError("Could not find xa/data/maniconfig.txt!")

def getVariable(variable):
    filename = "%s/%s" % (es.getAddonPath('xa'), 'data/maniconfig.txt')
    if os.path.exists(filename):
        lines = {}
        f = open(filename, "r")
        try:
            for line in f:
                linelist = line.split("|", 2)
                if linelist[0] == str(variable):
                    return es.ServerVar(linelist[0], linelist[1], linelist[2])
        finally:
            f.close()
        return None
    else:
        raise FileError("Could not find xa/data/maniconfig.txt!")
