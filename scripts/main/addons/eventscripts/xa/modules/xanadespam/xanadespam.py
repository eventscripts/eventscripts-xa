# ./xa/modules/xanadespam/xanadespam.py

import es
import playerlib
import services
from xa import xa


#######################################
# MODULE NAME
# This is the name of the module.
mymodulename = 'xanadespam'

# Register the module
# this is a global reference to our module
mymodule = xa.register(mymodulename)


#######################################
# SERVER VARIABLES
# The list of our server variables

punish_strip = mymodule.setting.createVariable('nadespam_punishment_strip', 0, '0 = do not strip weapons as punishment, 1 = strip weapons as punishment')
punish_cash  = mymodule.setting.createVariable('nadespam_punishment_cash', 0, '0 = do not remove cash as punishment, 1 = remove cash as punishment')
punish_slay  = mymodule.setting.createVariable('nadespam_punishment_slay', 0, '0 = do not slay as punishment, 1 = slay as punishment')
punish_kick  = mymodule.setting.createVariable('nadespam_punishment_kick', 0, '0 = do not kick as punishment, 1 = kick as punishment')

dict_grenade_limits = {'hegrenade':mymodule.setting.createVariable('nadespam_limit_he', 1, 'Maximum number of HE grenades players may purchase per round'), 'flashbang':mymodule.setting.createVariable('nadespam_limit_flashbang', 2, 'Maximum number of flashbangs players may purchase per round'), 'smokegrenade':mymodule.setting.createVariable('nadespam_limit_smoke', 1, 'Maximum number of smoke grenades players may purchase per round')}


#######################################
# GLOBALS
# Initialize our general global data here.

dict_players = {} # Number of each type of grenade a player has purchased
dict_grenade_names = {'he':'hegrenade', 'fb':'flashbang', 'sg':'smokegrenade'}
auth_service = services.use('auth')

# Localization helper:
func_lang_text = mymodule.language.getLanguage()


#######################################
# LOAD AND UNLOAD
# Formal system registration and unregistration
def load():
    auth_service.registerCapability('nadespam_immune', auth_service.ADMIN)
    mymodule.logging.log("XA module %s loaded." % mymodulename)


def unload():
    es.addons.unregisterClientCommandFilter(_cc_filter)

    mymodule.logging.log("XA module %s is being unloaded." % mymodulename)

    # Unregister the module
    xa.unregister(mymodule)


#######################################
# MODULE FUNCTIONS
# Register your module's functions


def round_start(event_var):
    """Initializes dictionary with the number of grenades each player starts the round with."""
    global dict_players

    dict_players.clear()
    for player in playerlib.getPlayerList('#all'):
        dict_current_player = dict_players[int(player)] = {}
        for str_grenade in dict_grenade_names:
            dict_current_player[dict_grenade_names[str_grenade]] = player.get(str_grenade)
round_start({})


def player_activate(event_var):
    """Creates the player in the dictionary"""
    global dict_players
    dict_players[int(event_var['userid'])] = {'hegrenade':0, 'flashbang':0, 'smokegrenade':0}


def player_disconnect(event_var):
    """Removes the disconnecting player from the dictionary."""
    global dict_players

    userid = int(event_var['userid'])
    if dict_players.has_key(userid):
        del dict_players[userid]


def _cc_filter(userid, args):
    """Eats the client command if the player tries to buy more grenades than allowed."""
    global dict_players

    if args[0].lower() == 'buy' and len(args) > 1:
        item = args[1].lower().replace('weapon_', '')
        if dict_grenade_limits.has_key(item):
            count = dict_players[userid][item] = dict_players[userid][item] + 1
            if count > dict_grenade_limits[item] and not auth_service.isUseridAuthorized(userid, 'nadespam_immune'):
                player = playerlib.getPlayer(userid)
                player_lang = player.get('lang')
                es.tell(userid, func_lang_text('limit %s' % item, {}, player_lang))

                if int(punish_strip):
                    es.server.queuecmd('es_xfire %s player_weaponstrip kill' % int_userid)
                    es.server.queuecmd('es_xgive %s player_weaponstrip' % int_userid)
                    es.server.queuecmd('es_xfire %s player_weaponstrip strip' % int_userid)

                if int(punish_cash):
                    player.set('cash', 0)

                if int(punish_slay):
                    player.kill()

                if int(punish_kick):
                    player.kick(func_lang_text('kick', {}, player_lang))

                return False
    return True

es.addons.registerClientCommandFilter(_cc_filter)
