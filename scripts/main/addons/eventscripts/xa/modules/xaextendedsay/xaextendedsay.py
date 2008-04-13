import es
import services
import playerlib
from xa import xa
from xa.modules.xasay import xasay

info                = es.AddonInfo() 
info.name           = "xaextendedsay" 
info.version        = "0.1" 
info.author         = "freddukes" 
info.url            = "http://forums.mattie.info" 
info.description    = "More options for the say feature for XA" 
info.tags           = "admin say players" 

xaextendedsay = xa.register('xaextendedsay') 
xalanguage    = xaextendedsay.language.getLanguage() 

def load(): 
    xasay.registerSayPrefix("@@" , _admin_say_tell) 
    xasay.registerSayPrefix("@@@", _admin_say_center) 
    
def _admin_say_tell(adminid, message, teamonly): 
    tokens = {} 
    userid = es.getuserid(message.split()[0]) 
    if userid: 
        tokens['adminname'] = es.getplayername(adminid) 
        tokens['username']  = es.getplayername(userid) 
        tokens['message']   = ' '.join(message.split()[1:]) 
        if not teamonly: 
            es.tell(userid , '#multi', xalanguage('admin to player', tokens, playerlib.getPlayer(userid).get("lang"))) 
            es.tell(adminid, '#multi', xalanguage('admin to player', tokens, playerlib.getPlayer(adminid).get("lang"))) 
        else: 
            es.centertell(userid , xalanguage('admin center to player', tokens, playerlib.getPlayer(userid).get("lang"))) 
            es.centertell(adminid, xalanguage('admin center to player', tokens, playerlib.getPlayer(adminid).get("lang"))) 
    else: 
        tokens['userid'] = userid 
        es.tell(adminid, '#multi', xalanguage('no player found', tokens, playerlib.getPlayer(adminid).get("lang"))) 
    return (0,'',0) 
    
def _admin_say_center(userid, message, teamonly): 
    tokens = {} 
    tokens['username'] = es.getplayername(userid) 
    tokens['message']  = message 
    if not teamonly: 
        for player in filter(lambda x: not es.getplayersteamid(x) == "BOT", es.getUseridList()): 
            es.centertell(player, xalanguage('center message', tokens, playerlib.getPlayer(player).get("lang"))) 
    else: 
        for player in playerlib.getPlayerList('#admin_say'): 
            es.centertell(int(player), xalanguage('admin only center message', tokens, player.get("lang"))) 
    return (0,'',0)
    
