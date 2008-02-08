import es
import os
import keyvalues
import xa

import psyco
psyco.full()

###########################
#Module methods start here#
###########################
def loadModules():
    filename = "%s/%s" % (es.getAddonPath('xa'), 'static/manimodule.txt')
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
        raise IOError, "Could not find xa/static/manimodule.txt!"
        
def loadVariables():
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
        raise IOError, "Could not find xa/static/maniconfig.txt!"
