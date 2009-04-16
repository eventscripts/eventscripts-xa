# ==============================================================================
#   IMPORTS
# ==============================================================================
# Python Imports
import os
import time

# EventScripts Imports
import es
import xa

# ==============================================================================
#   MODULE API FUNCTIONS
# ==============================================================================
def log(module, text, userid=None, admin=False):
    # Is logging enabled and does our module exist?
    if int(es.ServerVar('xa_log')) and xa.exists(module):
        # Was a valid source userid specified?
        if userid and es.exists('userid', int(userid)):
            # Is this userid an admin?
            if admin:
                # Adming log
                logtext = '%s: Admin %s [%s]: %s' % (module, es.getplayername(userid), es.getplayersteamid(userid), text)
            
            else:
                # User log
                logtext = '%s: User %s [%s]: %s' % (module, es.getplayername(userid), es.getplayersteamid(userid), text)
            
        else:
            # Default log
            logtext = '%s: %s' % (module, text)
        
        # Create our log folder if it does not exist
        if not os.path.isdir('%s/logs' % xa.coredir()):
            os.mkdir('%s/logs' % xa.coredir())
        
        # Write to our log file
        logname = '%s/logs/l%s' % (xa.coredir(), time.strftime('%m%d000.log'))
        logfile = open(logname, 'a+')
        logfile.write(time.strftime('L %m/%d/%Y - %H:%M:%S: ') + logtext + '\n')
        logfile.close()
        
        # Write to the SRCDS log file
        es.log(logtext)
