import es
import popuplib
import playerlib
import cfglib
import time
from xa import xa, logging

import os
import urllib2

#plugin information
info = es.AddonInfo()
info.name           = "XA Update Check"
info.version        = "1"
info.author         = "Errant"
info.basename       = "xaupdate"

#check_url = 'http://xa.eventscripts.com/api/version'
check_url = 'http://dev.xa.ojii.ch/api/version'
last_check = 'never'
remote_version = None
update_every = 86400

xamodule        = xa.register(info.basename)
xalanguage      = xamodule.language.getLanguage()


def load(): 
    # if we are loading xaupdate at the same time as server boot then we can safely run a check
    if (str(es.ServerVar('eventscripts_currentmap')) != ""):
        es_map_start({})
    else:
        # otherwise just create a dummy menu
        create_menu()
    xamodule.addMenu('xaupdate_menu', xalanguage['xaupdate'], 'xaupdate_menu', 'xaupdate_menu', 'ADMIN')
    
def es_map_start():
    if last_check == 'never' or (time.time()-last_check) > update_every:
        update_version()
        create_menu()
    
def create_menu():
    menu = popuplib.create('xaupdate_menu')
    menu.addline('XA Update Check')
    menu.addline(' ')
    menu.addline('XA Version:      %s' % xa.info.version)
    if remote_version:
        menu.addline('Current Release: %s' % remote_version)
    else:
        menu.addline('Current Release: %s' % remote_version)
    menu.addline(' ' )
    if last_check == 'never':
        menu.addline('Last checked:    %s' % last_check)
    else:
        menu.addline('Last checked:    %s' % time.strftime("%d/%m/%y %H:%M",time.gmtime(last_check)))
    menu.addline(' ')
    if xa.info.version != remote_version:
        menu.addline('A newer version is available!')
    else:
        menu.addline('XA is up to date')
    menu.addline(' ')
    menu.addline('->0. Close')
        
    
    
def update_version():
    global remote_version, last_check
    try:
        # try to open the check URL
        u = urllib2.urlopen(check_url)
        remote_version = u.read()
        last_check = time.time()
        logging.log('xaupdate','Retrieved latest version information from %s' %check_url)
        logging.log('xaupdate','Latest version is %s' %remote_version)
        if xa.info.version != remote_version:
            logging.log('xaupdate','There is a newer version of XA available')
        else:
            logging.log('xaupdate','XA is up to date')
    except HTTPError:
        # error
        logging.log('xaupdate','Unable to download version information')
