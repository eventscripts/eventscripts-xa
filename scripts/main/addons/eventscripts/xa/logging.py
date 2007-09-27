import es
import time

import xa

import psyco
psyco.full()

selfaddondir = str(es.server_var["eventscripts_addondir"]).replace("\\", "/")
selfmoddir = str(selfaddondir).rsplit("/", 2)[0] + '/'

selflogdir = "%s/logs/" % es.getAddonPath('xa')

###########################
#Module methods start here#
###########################
def log(module, text):
    if str(es.ServerVar("xa_log", 0, "Activates the module logging")) != '0':
        if str(module) in xa.gModules:
            logtext = str(module) + ': ' + str(text)
            logname = "%sl%s" % (selflogdir, time.strftime('%m%d000.log'))
            logfile = open(logname, 'a+')
            logfile.write(time.strftime('L %m/%d/%Y - %H:%M:%S: ') + logtext + '\n')
            logfile.close()
            es.log(logtext)
            return True
        else:
            return False
    else:
        return False
