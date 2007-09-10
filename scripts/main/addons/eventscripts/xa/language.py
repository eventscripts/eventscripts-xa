import es
import os
import langlib

import psyco
psyco.full()

selfaddondir = str(es.server_var["eventscripts_addondir"]).replace("\\", "/")
selfmoddir = str(selfaddondir).rsplit("/", 2)[0] + '/'

###########################
#Module methods start here#
###########################
def getLanguage(module=None,file=None):
    if module:
        if file:
            filename = "%s/module/%s/%s.ini" % (es.getAddonPath('xa'), module, file)
        else:
            filename = "%s/module/%s/strings.ini" % (es.getAddonPath('xa'), module)
    else:
        filename = "%s/language/strings.ini" % es.getAddonPath('xa')
    if os.path.exists(filename):
        return langlib.Strings(filename)
    else:
        raise FileError("Could not find %s!" % filename)
