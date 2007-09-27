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
