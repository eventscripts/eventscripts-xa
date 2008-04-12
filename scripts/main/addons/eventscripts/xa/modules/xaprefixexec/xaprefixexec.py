# ./xa/modules/xaprefixexec/xaprefixexec.py

import es
import os
from xa import xa

"""
Executes ./cfg/xa/xaprefixexec/<map prefix>.cfg every map
"""


#######################################
# MODULE NAME
# This is the name of the module.
mymodulename = 'xaprefixexec'

# Register the module
# this is a global reference to our module
mymodule = xa.register(mymodule)


#######################################
# GLOBALS
# Initialize our general global data here.

str_dir = None # Directory of the .cfg files


#######################################
# LOAD AND UNLOAD
# Formal system registration and unregistration

def load():
    """
    Ensures the .cfg directories exist
    Loads the path to the .cfg directory in str_dir
    """
    global str_dir
    mymodule.logging.log('XA module %s loaded.' % mymodulename)

    # Ensures .cfg directories exist
    str_dir = es.ServerVar('eventscripts_gamedir') + '/cfg/xa'
    _check_directory(str_dir)
    str_dir += '/%s' % mymodulename
    _check_directory(str_dir)


def unload():
    mymodule.logging.log('XA module %s is being unloaded.' % mymodulename)

    # Unregister the module
    xa.unregister(mymodule)


#######################################
# MODULE FUNCTIONS
# Register your module's functions

def es_map_start(event_var):
    """Executes ./cfg/xa/xaprefixexec/<map prefix>.cfg"""
    str_mapname = event_var['mapname']
    if '_' in str_mapname: # No prefix, no .cfg
        str_prefix = str_mapname.split('_')[0]
        if os.path.isfile(str_dir + '/%s.cfg' % str_prefix):
            es.server.queuecmd('exec xa/%s/%s.cfg' % (mymodulename, str_prefix))


def _check_directory(str_dir):
    """Creates the directory if it doesn't exist"""
    if not os.path.isdir(str_dir):
        os.mkdir(str_dir)
