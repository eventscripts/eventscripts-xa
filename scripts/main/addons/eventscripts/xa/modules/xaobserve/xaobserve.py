# ./xa/modules/xaobserve/xaobserve.py

"""
TODO: Allow admin-view with mp_forcecamera
"""


import es
import gamethread
import playerlib
import random
import services
from xa import xa


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

var_allow_chase = mymodule.setting.createVariable('observe_allow_chase', 1, 'xaobserve: 0 = only allow first-person view for dead players, 1 = allow frist-person or chase-cam view for dead players')
var_spec_delay = mymodule.setting.createVariable('observe_spec_delay', 3, 'xaobserve: Number of seconds after death a player can be spectated')


#######################################
# GLOBALS
# We initialize our general global data here.

# Module globals
list_delays = []
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

    mymodule.logging.log('XA module %s loaded.' % mymodulename)

    auth_service = services.use('auth')
    auth_service.registerCapability('opponent_observe', auth_service.ADMIN)

    round_start({})


def unload():
    """
    Unregisters the module with XA
    Cancels outstanding delays and unregisters client command filter
    """
    mymodule.logging.log('XA module %s unloaded.' % mymodulename)

    # Unregister the module
    xa.unregister(mymodule)

    cancel_delays()


#######################################
# MODULE FUNCTIONS
# xaobserver module functions

def round_start(event_var):
    """
    Cancels outstanding delays and unregisters client command filter
    Refreshes the dictionary of living player handles
    """
    global dict_team_handles

    cancel_delays()

    dict_team_handles = {2:[], 3:[]}
    for int_userid in es.getUseridList():
        add_player_handle(int_userid, es.getplayerteam(int_userid))


def player_spawn(event_var):
    """Ensures the player's handle is in the dictionary of living player handles and not in the dictionary of dead players"""
    add_player_handle(int(event_var['userid']), int(event_var['es_userteam']))


def player_death(event_var):
    """
    Removes the dead player's handle from the dictionary of living player handles
    Registers client command filter if this is the first unauthorized dead player
    Adds the player to the dictionary of dead players to monitor if the player is not authorized to observe opponents
    """
    global dict_dead_players

    int_userid = int(event_var['userid'])
    int_team = int(event_var['es_userteam'])
    int_handle = es.getplayerhandle(int_userid)

    if dict_team_handles.has_key(int_team):
        for int_loop_userid in dict_dead_players:
            if dict_dead_players[int_loop_userid] == int_handle:
                gamethread.delayedname(float(var_spec_delay), 'xaobserve_%s' % int_loop_userid, end_spec_delay, int_loop_userid)

        if int_handle in dict_team_handles[int_team]:
            dict_team_handles[int_team].remove(int_handle)

    if not auth_service.isUseridAuthorized(int_userid, 'opponent_observe') and event_var['es_steamid'] <> 'BOT':
        if not dict_dead_players:
            es.addons.registerClientCommandFilter(client_command_filter)

        dict_dead_players[int_userid] = -1
        gamethread.delayedname(float(var_spec_delay), 'xaobserve_%s' % int_userid, end_spec_delay, (int_userid, True))
        if int_userid not in list_delays:
            list_delays.append(int_userid)


def player_disconnect(event_var):
    """
    Cancels any delays for the disconnecting player
    Removes the disconnecting player from the dictionary of unauthorized dead players
    """
    global dict_dead_players

    int_userid = int(event_var['userid'])
    if int_userid in list_delays:
        gamethread.cancelDelayed('xaobserve_%s' % int_userid)
        list_delays.remove(int_userid)

    if dict_dead_players.has_key(int_userid):
        del dict_dead_players[int_userid]
        if not dict_dead_players:
            es.addons.unregisterClientCommandFilter(client_command_filter)


def client_command_filter(int_userid, list_args):
    """
    Checks all non-admin dead players for spectating an opponent
    """
    global dict_dead_players

    int_team = es.getplayerteam(int_userid)
    if not dict_dead_players.has_key(int_userid) or not list_args or int_team not in (2, 3):
        return 1

    if int_userid in list_delays:
        gamethread.cancelDelayed('xaobserve_%s' % int_userid)
        list_delays.remove(int_userid)

    if list_args[0] == 'spec_mode':
        if es.getplayerprop(int_userid, 'CBasePlayer.m_iObserverMode') == 3 and int(var_allow_chase):
            es.setplayerprop(int_userid, 'CBasePlayer.m_iObserverMode', 4)
        else:
            es.setplayerprop(int_userid, 'CBasePlayer.m_iObserverMode', 3)
        return 0

    elif list_args[0] == 'spec_next' and dict_team_handles[int_team]:
        int_target_handle = es.getplayerprop(int_userid, 'CBasePlayer.m_hObserverTarget')
        if int_target_handle in dict_team_handles[int_team]:
            int_target_index = dict_team_handles[int_team].index(int_target_handle) + 1
            if int_target_index >= len(dict_team_handles[int_team]):
                int_target_index = 0
            dict_dead_players[int_userid] = dict_team_handles[int_team][int_target_index]
        else:
            dict_dead_players[int_userid] = dict_team_handles[int_team][0]
        es.setplayerprop(int_userid, 'CBasePlayer.m_hObserverTarget', dict_dead_players[int_userid])
        return 0

    elif list_args[0] == 'spec_prev' and dict_team_handles[int_team]:
        int_target_handle = es.getplayerprop(int_userid, 'CBasePlayer.m_hObserverTarget')
        if int_target_handle in dict_team_handles[int_team]:
            int_target_index = dict_team_handles[int_team].index(int_target_handle) - 1
            if int_target_index < 0:
                int_target_index = len(dict_team_handles[int_team]) - 1
            dict_dead_players[int_userid] = dict_team_handles[int_team][int_target_index]
        else:
            dict_dead_players[int_userid] = dict_team_handles[int_team][0]
        es.setplayerprop(int_userid, 'CBasePlayer.m_hObserverTarget', dict_dead_players[int_userid])
        return 0

    return 1


def end_spec_delay(int_userid, bool_set_mode=False):
    """
    Removes the delay from the list of delays
    Forces the client to spectate a teammate
    """
    if int_userid in list_delays:
        list_delays.remove(int_userid)

    if bool_set_mode:
        client_command_filter(int_userid, ['spec_mode'])
    client_command_filter(int_userid, ['spec_next'])


def add_player_handle(int_userid, int_team):
    """Adds the player's handle to the dictionary of player handles according to team"""
    global dict_dead_players
    global dict_team_handles

    if int_team in (2, 3):
        int_handle = es.getplayerhandle(int_userid)
        if int_handle not in dict_team_handles[int_team]:
            dict_team_handles[int_team].append(int_handle)

    if playerlib.getPlayer(int_userid).get('isdead'):
        dict_dead_players[int_userid] = -1
        end_spec_delay(int_userid)

    elif dict_dead_players.has_key(int_userid):
        del dict_dead_players[int_userid]


def cancel_delays():
    """
    Cancels delays for dead players
    Unregisters client command filter
    """
    global list_delays

    for int_userid in list_delays:
        gamethread.cancelDelayed('xaobserve_%s' % int_userid)

    if dict_dead_players:
        es.addons.unregisterClientCommandFilter(client_command_filter)
        dict_dead_players.clear()
