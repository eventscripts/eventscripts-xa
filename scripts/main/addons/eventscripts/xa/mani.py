import es
import os

import psyco
psyco.full()

selfaddondir = str(es.server_var["eventscripts_addondir"]).replace("\\", "/")
selfmoddir = str(selfaddondir).rsplit("/", 2)[0] + '/'

###########################
#Module methods start here#
###########################
def loadModules():
    filename = "%s/%s" % (es.getAddonPath('xa'), 'data/mani.txt')
    if os.path.exists(filename):
        f = open(filename, "r")
        try:
            for line in f:
                linelist = line.split("|", 2)
                variable = es.ServerVar(linelist[0], 0)
                if linelist[2] == str(variable):
                    if not es.exists("script", "xa/module/"+linelist[2]):
                        es.load("xa/module/"+linelist[2])
        finally:
            f.close()
    else:
        raise FileError("Could not find xa/data/mani.txt!")
