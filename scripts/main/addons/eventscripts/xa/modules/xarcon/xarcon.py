# ./xa/modules/xarcon/xarcon.py

import es
from xa import xa


#######################################
# MODULE NAME

# This is the name of the module.
mymodulename = 'xarcon'

# Register the module
# this is a global reference to our module
mymodule = xa.register(mymodulename)


#######################################
# GLOBALS
# We initialize our general global data here.

list_round_rcon = []
list_map_rcon = []


#######################################
# LOAD AND UNLOAD
# Formal system registration and unregistration
def load():
    """Registers the xarcon commands"""
    mymodule.logging.log('XA module %s loaded.' % mymodulename)

    mymodule.addCommand('xa_rcon', rcon_cmd, 'use_rcon', '#root', descr="Appends the command to the end of the queue of server commands to execute").register(('say', 'console'))
    mymodule.addCommand('xa_rcon_round', rcon_round_cmd, 'use_rcon', '#root', descr="Appends the command to the end of the queue of server commands to execute next round").register(('say', 'console'))
    mymodule.addCommand('xa_rcon_map', rcon_map_cmd, 'use_rcon', '#root', descr="Appends the command to the end of the queue of server commands to execute next map").register(('say', 'console'))


def unload():
    """Unregisters the module with XA"""
    mymodule.logging.log('XA module %s unloaded.' % mymodulename)

    # Unregister the module
    xa.unregister(mymodule)


#######################################
# MODULE FUNCTIONS
# Register your module's functions

def es_map_start(event_var):
    """Executes all xarcon_map commands"""
    global list_map_rcon

    for str_item in list_map_rcon:
        es.server.queuecmd(str_item)
    list_map_rcon[:] = []


def round_start(event_var):
    """Executes all xarcon_round commands"""
    global list_round_rcon

    for str_item in list_round_rcon:
        es.server.queuecmd(str_item)
    list_round_rcon[:] = []


def rcon_cmd():
    """Appends the command to the end of the queue of server commands to execute"""
    es.server.queuecmd(es.getargs())


def rcon_round_cmd():
    """Appends the command to the end of the queue of server commands to execute next round"""
    list_round_rcon.append(es.getargs())


def rcon_map_cmd():
    """Appends the command to the end of the queue of server commands to execute next map"""
    list_map_rcon.append(es.getargs())
