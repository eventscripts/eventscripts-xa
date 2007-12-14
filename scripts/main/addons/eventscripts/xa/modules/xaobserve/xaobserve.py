# ./xa/modules/xaobserve/xaobserve.py

"""
TODO: Force mode
"""


import es
import random
import services
import xa
import xa.setting
import xa.logging


#######################################
# MODULE NAME
# This is the name of the module.

mymodulename = 'xaobserve'

# Register the module
# this is a global reference to our module

mymodule = xa.register(mymodulename)


#######################################
# SERVER VARIABLES
# The list of our server variables

tick_delay = xa.setting.createVariable('observe_tick_delay', 5, 'xaobserve: Number of game ticks between enforecment of observer rules')


#######################################
# GLOBALS
# We initialize our general global data here.

int_tick_count = 0
dict_dead_players = {}
dict_team_handles = {2:[], 3:[]}
auth_service = None


#######################################
# LOAD AND UNLOAD
# Formal system registration and unregistration

def load():
    """
    Logs the module load with XA
    Registers the "opponent_observe" ability with the authorization service
    """
    global auth_service

    xa.logging.log(mymodule, 'XA module %s loaded.' % mymodulename)

    auth_service = services.use('auth')
    auth_service.registerCapability('opponent_observe', auth_service.ADMIN)

    round_start({})


def unload():
    """
    Unregisters the module with XA
    Unregisters the tick listener
    """
    xa.logging.log(mymodule, 'XA module %s unloaded.' % mymodulename)

    # Unregister the module
    xa.unregister(mymodulename)

    unregister_tick()


#######################################
# MODULE FUNCTIONS
# xaobserver module functions

def round_start(event_var):
    """
    Refreshes the dictionary of living player handles
    Unregisters the tick lister
    """
    global dict_team_handles

    dict_team_handles = {2:[], 3:[]}
    for int_userid in es.getUseridList():
        add_player_handle(int(event_var['userid']), es.getplayerteam(int_userid))

    unregister_tick()


def player_spawn(event_var):
    """Ensures the player's handle is in the dictionary of living player handles"""
    add_player_handle(int(event_var['userid']), int(event_var['es_userteam']))


def player_death(event_var):
    """
    Removes the dead player's handle from the dictionary of living player handles
    Adds the player to the dictionary of dead players to monitor if the player is not authorized to observe opponents
    Registers the tick listener if this is the first unauthorized dead player
    """
    global dict_dead_players

    int_userid = int(event_var['userid'])
    int_team = int(event_var['es_userteam'])
    if dict_team_handles.has_key(int_team):
        int_handle = es.getplayerhandle(int_userid)
        if int_handle in dict_team_handles[int_team]:
            dict_team_handles[int_team].remove(int_handle)

    if not auth_service.isUseridAuthorized(int_userid, 'opponent_observe') and event_var['es_steamid'] <> 'BOT':
        if not dict_dead_players:
            es.addons.registerTickListener(tick)
        dict_dead_players[int_userid] = int_team


def tick():
    """
    Checks all non-admin dead players for spectating an opponent
    """
    global int_tick_count

    int_tick_count += 1
    if int_tick_count >= int(tick_delay):
        int_tick_count = 0

        for int_userid in dict_dead_players:
            int_team = dict_dead_players[int_userid]
            if es.getplayerprop(int_userid, 'CBasePlayer.m_hObserverTarget') in dict_team_handles[5 - int_team] and dict_team_handles[int_team]:
                es.setplayerprop(int_userid, 'CBasePlayer.m_hObserverTarget', random.choice(dict_team_handles[int_team]))


def add_player_handle(int_userid, int_team):
    """Adds the player's handle to the dictionary of player handles according to team"""
    global dict_team_handles

    if int_team in (2, 3):
        int_handle = es.getplayerhandle(int_userid)
        if int_handle not in dict_team_handles[int_team]:
            dict_team_handles[int_team].append(int_handle)


def unregister_tick():
    """Unregisters the tick listener if it is registered"""
    if dict_dead_players:
        es.addons.unregisterTickListener(tick)
        dict_dead_players.clear()