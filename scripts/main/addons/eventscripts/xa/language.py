import es
import os
import langlib

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
def getLanguage(module = None, file = None):
    if module:
        if file:
            filename = "%s/modules/%s/%s.ini" % (es.getAddonPath('xa'), module, file)
        else:
            filename = "%s/modules/%s/strings.ini" % (es.getAddonPath('xa'), module)
    else:
        filename = "%s/languages/strings.ini" % es.getAddonPath('xa')
    if os.path.exists(filename):
        return langlib.Strings(filename)
    else:
        raise IOError, "Could not find %s!" % filename
