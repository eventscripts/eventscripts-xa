import es
import repeat
import xa
import xa.setting
import playerlib
from xa import xa

#plugin information
info = es.AddonInfo() 
info.name     = 'High Ping Kicker - XA Module' 
info.version  = 'oy2' 
info.url      = 'http://mattie.info/cs' 
info.basename = 'highpingkick' 
info.author   = 'SumGuy14 (Aka SoccerDude)'

gInfo = {}

# register module with XA
xahighpingkick = xa.register('xahighpingkick')

# make config vars
maxping       = xa.setting.createVariable(xahighpingkick,'ping_maxping', '300', 'Maximum ping of a player before they are kicked')
check         = xa.setting.createVariable(xahighpingkick,'ping_check', '10', 'How many total times to check the players ping over a period of time before they are kicked')
interval      = xa.setting.createVariable(xahighpingkick,'ping_interval', '5', 'How often the players ping is checked, in seconds')
exceedlimit   = xa.setting.createVariable(xahighpingkick,'ping_exceedlimit', '3', 'If the players ping is above the max when checked this many times, player will be kicked')
kickmsg       = xa.setting.createVariable(xahighpingkick,'ping_kickmsg', 'Your ping is too high!', 'Message displayed to kicked player')

def unload(): 
    xa.unRegister('xahighpingkick') 

def player_activate(event_var):
    userid = event_var['userid']
    gInfo[userid] = 0
    myRepeat = repeat.create('hpk_track_' + userid,tracker,userid)
    myRepeat.start(interval,check)

def player_disconnect(event_var):
    userid = event_var['userid']
    status = repeat.status('hpk_track_' + userid)
    if status != 0:
        myrepeat = repeat.find('hpk_track_' + userid)
        myrepeat.delete()

def tracker(userid,info):
    if es.exists('userid',userid):
        ping = es.createplayerlist(userid)[int(userid)]['ping']
        if ping >= maxping:
            gInfo[userid]+=1
        if gInfo[userid] >= exceedlimit:
            slowguy = playerlib.getPlayer(userid)
            slowguy.kick(reason=kickmsg)
    else:
        myRepeat = info[0]
        myRepeat.delete()
    
