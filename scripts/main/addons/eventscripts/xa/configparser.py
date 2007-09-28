import es
import os
import keyvalues

import xa

import psyco
psyco.full()

selfaddondir = str(es.server_var["eventscripts_addondir"]).replace("\\", "/")
selfmoddir = str(es.server_var["eventscripts_gamedir"]).replace("\\", "/")

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
