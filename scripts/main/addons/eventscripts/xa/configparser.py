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
########################################################
# All methods that should be able to be called through #
# the API need to have "module" as first parameter     #
########################################################
def getList(module, filename, modfolder = False):
    if str(module) in xa.gModules:
        if modfolder == False:
            filename = "%s/cfg/xa/%s/%s" % (selfmoddir, str(module), filename)
        else:
            filename = "%s/%s" % (selfmoddir, filename)
        filename = filename.replace("\\", "/")
        if os.path.exists(filename):
            lines = []
            f = open(filename, "r")
            try:
                for line in f:
                    if (len(line) > 0) and (line[0:2] != '//') and (line != '\n'):
                        line = line.replace("\n", "")
                        line = line.replace("\t", " ")
                        line = line.replace("  ", " ")
                        lines.append(line)
            finally:
                f.close()
            return lines
        else:
            return False
    else:
        return False

def getAliasList(module, filename, modfolder = False):
    if str(module) in xa.gModules:
        if modfolder == False:
            filename = "%s/cfg/xa/%s/%s" % (selfmoddir, str(module), filename)
        else:
            filename = "%s/%s" % (selfmoddir, filename)
        filename = filename.replace("\\", "/")
        if os.path.exists(filename):
            lines = {}
            f = open(filename, "r")
            try:
                for line in f:
                    if (len(line) > 0) and (line[0:2] != '//') and (line != '\n'):
                        line = line.replace("\n", "")
                        line = line.replace("\t", " ")
                        line = line.replace("  ", " ")
                        line = line[1:]
                        linelist = line.split("\" ", 1)
                        lines[linelist[0].replace("\"", "")] = linelist[1]
            finally:
                f.close()
            return lines
        else:
            return False
    else:
        return False
            
def getKeyList(module, filename, modfolder = False):
    if str(module) in xa.gModules:
        if modfolder == False:
            filename = "%s/cfg/xa/%s/%s" % (selfmoddir, str(module), filename)
        else:
            filename = "%s/%s" % (selfmoddir, filename)
        filename = filename.replace("\\", "/")
        if os.path.exists(filename):
            kv = keyvalues.KeyValues(name=basename(filename))
            kv.load(filename)
            return kv
        else:
            return False
    else:
        return False
