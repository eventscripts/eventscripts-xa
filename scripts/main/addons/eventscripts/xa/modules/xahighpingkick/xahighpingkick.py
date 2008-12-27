import es
import repeat
import playerlib
from xa import xa

#plugin information
info = es.AddonInfo() 
info.name     = 'High Ping Kicker - XA Module' 
info.version  = 'oy2' 
info.url      = 'http://forums.mattie.info' 
info.basename = 'xahighpingkick' 
info.author   = 'SumGuy14 (Aka SoccerDude)'

gInfo = {}

# register module with XA
xahighpingkick = xa.register('xahighpingkick')

# Localization helper:
text = xahighpingkick.language.getLanguage()

# make config vars
maxping       = xahighpingkick.setting.createVariable('ping_maxping', 300, 'Maximum ping of a player before they are kicked')
check         = xahighpingkick.setting.createVariable('ping_check', 10, 'How many total times to check the players ping over a period of time before they are kicked')
interval      = xahighpingkick.setting.createVariable('ping_interval', 5, 'How often the players ping is checked, in seconds')
exceedlimit   = xahighpingkick.setting.createVariable('ping_exceedlimit', 3, 'If the players ping is above the max when checked this many times, player will be kicked')

def unload(): 
    for userid in es.getUseridList():
        if repeat.status('hpk_track_' + userid) != 0:
            repeat.find('hpk_track_' + userid).delete()
    xahighpingkick.unregister() 

def player_activate(event_var):
    userid = event_var['userid']
    gInfo[userid] = 0
    repeat.create('hpk_track_' + userid,tracker,userid).start(float(interval),float(check))

def player_disconnect(event_var):
    userid = event_var['userid']
    if repeat.status('hpk_track_' + userid) != 0:
        repeat.find('hpk_track_' + userid).delete()

def tracker(userid, info = None):
    if es.exists('userid',userid):
        ping = es.createplayerlist(userid)[int(userid)]['ping']
        if maxping and ping >= int(maxping):
            gInfo[userid]+=1
        if exceedlimit and gInfo[userid] >= int(exceedlimit):
            slowguy = playerlib.getPlayer(userid)
            slowguy.kick(reason=text('kick', {}, slowguy.get('lang')))
    elif info is not None:
        info[0].delete()
