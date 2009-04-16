import es
import os
import time
import xa

###########################
#Module methods start here#
###########################
def log(module, text, userid=0, admin=False):
    if bool(int(es.ServerVar("xa_log"))) and xa.exists(module):
        if (int(userid) > 0) and es.exists('userid', int(userid)):
            if admin:
                logtext = str(module) + ': Admin ' + es.getplayername(userid) + ' [' + es.getplayersteamid(userid) + ']: ' + str(text)
            else:
                logtext = str(module) + ': User ' + es.getplayername(userid) + ' [' + es.getplayersteamid(userid) + ']: ' + str(text)
        else:
            logtext = str(module) + ': ' + str(text)
        if not os.path.isdir('%s/logs' % xa.coredir()):
            os.mkdir('%s/logs' % xa.coredir())
        logname = '%s/logs/l%s' % (xa.coredir(), time.strftime('%m%d000.log'))
        logfile = open(logname, 'a+')
        logfile.write(time.strftime('L %m/%d/%Y - %H:%M:%S: ') + logtext + '\n')
        logfile.close()
        es.log(logtext)
        return True
    return False
