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
        full = langlib.getLanguages()
        defl = langlib.getDefaultLang()
        lang = langlib.Strings(filename)
        ####################################################################
        ## ADD LANGUAGE PLACEHOLDERS FOR EASYMENUS -- BAD WAY -> OVERHEAD ##
        ####################################################################
        for k in lang:
            for l in full:
                i = full[l]["id"]
                if not i in lang[k]:
                    if defl in lang[k]:
                        lang[k][i] = lang[k][defl]
                    elif "en" in lang[k]:
                        lang[k][i] = lang[k]["en"]
        ####################################################################
        return lang
    else:
        raise IOError, "Could not find %s!" % filename
