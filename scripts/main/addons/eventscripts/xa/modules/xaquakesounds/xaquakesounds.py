import es
import os
import time
import xa
import xa.configparser
import xa.setting
import xa.modules.xasettings.xasettings
from xa import xa

timer = {}
playerkills = {}
firstblood = False

#plugin information
info = es.AddonInfo()
info.name           = "XA:Quake Sounds"
info.version        = "0.1"
info.author         = "Hunter"
info.url            = "http://forums.mattie.info/"
info.description    = "Clone of Mani Quake Sounds feature for XA"
info.tags           = "admin quake sounds XA"

xaquakesounds                       = xa.register('xaquakesounds')
xalanguage                          = xa.language.getLanguage('xaquakesounds')
xaquakesoundslist                   = xa.configparser.getAliasList('xaquakesounds', 'quakesoundlist.txt')
quake_sounds                        = xa.setting.createVariable('xaquakesounds', 'quake_sounds', '0')
quake_kill_streak_mode              = xa.setting.createVariable('xaquakesounds', 'quake_kill_streak_mode', '0')
quake_humiliation_mode              = xa.setting.createVariable('xaquakesounds', 'quake_humiliation_mode', '1')
quake_humiliation_visual_mode       = xa.setting.createVariable('xaquakesounds', 'quake_humiliation_visual_mode', '1')
quake_humiliation_weapon            = xa.setting.createVariable('xaquakesounds', 'quake_humiliation_weapon', 'knife')
quake_humiliation_weapon2           = xa.setting.createVariable('xaquakesounds', 'quake_humiliation_weapon2', '')
quake_firstblood_mode               = xa.setting.createVariable('xaquakesounds', 'quake_firstblood_mode', '1')
quake_firstblood_visual_mode        = xa.setting.createVariable('xaquakesounds', 'quake_firstblood_visual_mode', '1')
quake_firstblood_reset_per_round    = xa.setting.createVariable('xaquakesounds', 'quake_firstblood_reset_per_round', '1')
quake_headshot_mode                 = xa.setting.createVariable('xaquakesounds', 'quake_headshot_mode', '3')
quake_headshot_visual_mode          = xa.setting.createVariable('xaquakesounds', 'quake_headshot_visual_mode', '3')
quake_prepare_to_fight_mode         = xa.setting.createVariable('xaquakesounds', 'quake_prepare_to_fight_mode', '1')
quake_prepare_to_fight_visual_mode  = xa.setting.createVariable('xaquakesounds', 'quake_prepare_to_fight_visual_mode', '1')
quake_multi_kill_mode               = xa.setting.createVariable('xaquakesounds', 'quake_multi_kill_mode', '1')
quake_multi_kill_visual_mode        = xa.setting.createVariable('xaquakesounds', 'quake_multi_kill_visual_mode', '1')
quake_team_killer_mode              = xa.setting.createVariable('xaquakesounds', 'quake_team_killer_mode', '1')
quake_team_killer_visual_mode       = xa.setting.createVariable('xaquakesounds', 'quake_team_killer_visual_mode', '1')

xaquakekills = {}
xaquakekills['dominating'] = {}
xaquakekills['dominating']['mode']            = xa.setting.createVariable('xaquakesounds', 'quake_dominating_mode', '3')
xaquakekills['dominating']['visual_mode']     = xa.setting.createVariable('xaquakesounds', 'quake_dominating_visual_mode', '3')
xaquakekills['dominating']['trigger_count']   = xa.setting.createVariable('xaquakesounds', 'quake_dominating_trigger_count', '4')
xaquakekills['rampage'] = {}
xaquakekills['rampage']['mode']               = xa.setting.createVariable('xaquakesounds', 'quake_rampage_mode', '1')
xaquakekills['rampage']['visual_mode']        = xa.setting.createVariable('xaquakesounds', 'quake_rampage_visual_mode', '1')
xaquakekills['rampage']['trigger_count']      = xa.setting.createVariable('xaquakesounds', 'quake_rampage_trigger_count', '6')
xaquakekills['killingspree'] = {}
xaquakekills['killingspree']['mode']          = xa.setting.createVariable('xaquakesounds', 'quake_killing_spree_mode', '3')
xaquakekills['killingspree']['visual_mode']   = xa.setting.createVariable('xaquakesounds', 'quake_killing_spree_visual_mode', '3')
xaquakekills['killingspree']['trigger_count'] = xa.setting.createVariable('xaquakesounds', 'quake_killing_spree_trigger_count', '8')
xaquakekills['monsterkill'] = {}
xaquakekills['monsterkill']['mode']           = xa.setting.createVariable('xaquakesounds', 'quake_monster_kill_mode', '3')
xaquakekills['monsterkill']['visual_mode']    = xa.setting.createVariable('xaquakesounds', 'quake_monster_kill_visual_mode', '3')
xaquakekills['monsterkill']['trigger_count']  = xa.setting.createVariable('xaquakesounds', 'quake_monster_kill_trigger_count', '10')
xaquakekills['unstoppable'] = {}
xaquakekills['unstoppable']['mode']           = xa.setting.createVariable('xaquakesounds', 'quake_unstoppable_mode', '1')
xaquakekills['unstoppable']['visual_mode']    = xa.setting.createVariable('xaquakesounds', 'quake_unstoppable_visual_mode', '1')
xaquakekills['unstoppable']['trigger_count']  = xa.setting.createVariable('xaquakesounds', 'quake_unstoppable_trigger_count', '12')
xaquakekills['ultrakill'] = {}
xaquakekills['ultrakill']['mode']             = xa.setting.createVariable('xaquakesounds', 'quake_ultra_kill_mode', '1')
xaquakekills['ultrakill']['visual_mode']      = xa.setting.createVariable('xaquakesounds', 'quake_ultra_kill_visual_mode', '1')
xaquakekills['ultrakill']['trigger_count']    = xa.setting.createVariable('xaquakesounds', 'quake_ultra_kill_trigger_count', '14')
xaquakekills['godlike'] = {}
xaquakekills['godlike']['mode']               = xa.setting.createVariable('xaquakesounds', 'quake_god_like_mode', '1')
xaquakekills['godlike']['visual_mode']        = xa.setting.createVariable('xaquakesounds', 'quake_god_like_visual_mode', '1')
xaquakekills['godlike']['trigger_count']      = xa.setting.createVariable('xaquakesounds', 'quake_god_like_trigger_count', '16')
xaquakekills['wickedsick'] = {}
xaquakekills['wickedsick']['mode']            = xa.setting.createVariable('xaquakesounds', 'quake_wicked_sick_mode', '1')
xaquakekills['wickedsick']['visual_mode']     = xa.setting.createVariable('xaquakesounds', 'quake_wicked_sick_visual_mode', '1')
xaquakekills['wickedsick']['trigger_count']   = xa.setting.createVariable('xaquakesounds', 'quake_wicked_sick_trigger_count', '18')
xaquakekills['ludicrouskill'] = {}
xaquakekills['ludicrouskill']['mode']         = xa.setting.createVariable('xaquakesounds', 'quake_ludicrous_kill_mode', '1')
xaquakekills['ludicrouskill']['visual_mode']  = xa.setting.createVariable('xaquakesounds', 'quake_ludicrous_kill_visual_mode', '1')
xaquakekills['ludicrouskill']['trigger_count']= xa.setting.createVariable('xaquakesounds', 'quake_ludicrous_kill_trigger_count', '20')
xaquakekills['holyshit'] = {}
xaquakekills['holyshit']['mode']              = xa.setting.createVariable('xaquakesounds', 'quake_holy_shit_mode', '1')
xaquakekills['holyshit']['visual_mode']       = xa.setting.createVariable('xaquakesounds', 'quake_holy_shit_visual_mode', '1')
xaquakekills['holyshit']['trigger_count']     = xa.setting.createVariable('xaquakesounds', 'quake_holy_shit_trigger_count', '24')

def unload():
    xa.unRegister(xaquakesounds)

def es_map_start():
    firstblood = True

def round_start(event_var):
    if int(quake_firstblood_reset_per_round) == 1:
        firstblood = True
    for userid in es.getUseridList():
        if (not userid in playerkills) or (quake_kill_streak_mode == 1):
            playerkills[userid] = 0

def player_spawn(event_var):
    userid = int(event_var['userid'])
    if not userid in playerkills:
        playerkills[userid] = 0

def player_death(event_var):
    userid = int(event_var['userid'])
    attackerid = int(event_var['attacker'])
    if userid > 0:
        playerkills[userid] = 0
    if attackerid > 0:
        if attackerid in playerkills:
            playerkills[attackerid] += 1
        else:
            playerkills[attackerid] = 1
    if firstblood == True:
        firstblood = False
        if int(quake_firstblood_mode) == 1:
            pass
