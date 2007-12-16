import es
import xa
import xa.language
import xa.logging
import xa.playerdata
import xa.setting
from xa import xa 
import playerlib
import repeat
import usermsg

global blinded
blinded = {}


#plugin information
info = es.AddonInfo()
info.name = "XA:IP Ghosting"
info.version = "1.0"
info.author = "Errant"
info.url = "http://forums.mattie.info/cs/forums/viewtopic.php?t=16321"
info.description = "Clone of Mani's IP ghosting feature for XA"
info.tags = "admin ip ghosting player_death XA"

'''
==  XA:IP Ghosting - A full port of mani's fuctionality to blind IP ghosters  ==
 
-- About --

 - Supports the original mani cfg variable (to turn it on and off bascially)
 - Does NOT currently support (as mani did) disabling votekick and voteban functionality for ghosters - mostly as there is no XA Vote module yet!
 
-- Version log --
 #    |  Type  | Date       |  Change log
OY1   | [BETA] | 15/09/2007 |  Working Standalone version
1.0   | [FULL] | 08/10/2007 |  Converted to work within XA, added multi-lingual functionality
1.0.1 | [FULL] | 15/11/2007 | [FIX] r_screenoverlay requires a cheat - changed to use 1 1sec repeated fade via usermsg.fade (works v well - thx to Mattie for the idea)


--Future--
 #  |  Status       | Desc
1.5 | [UNSTARTED]   | Add other features, provide admin notification / features, add further config options
'''

def repeat_fade(x):
    '''
    Method to handle the fading. Is run every second by the repeat xaip. 
    The fade is set to fade out so on round end you get a nice fade out effect for the player
    '''
    global blinded
    for userid in blinded:
        es.msg(userid)
        usermsg.fade(userid,1,500,1000,0,0,0,255)

def blindplayer(self, uid):
    '''
    - Starts the fade repeat if it isn't already running
    - Fades out the player
    - Adds their userid to the dictionary so they are kept faded out
    - Tell them 3 times they have been blinded
    '''
    plib = playerlib.getPlayer(uid) 
    if repeat.status("xaip") == 0:
        a = repeat.create("xaip", repeat_fade)
        a.start(1,0)
    # do the initial fade 
    usermsg.fade(uid,2,500,1000,0,0,0,255)
    # add them to the usergroup
    blinded[uid] = 1
    # Annnnd tell them about it
    es.tell(int(plib), text("blind_message",None,plib.get("lang")))
    es.tell(int(plib), text("blind_message",None,plib.get("lang")))
    es.tell(int(plib), text("blind_message",None,plib.get("lang")))

def checkplayer(uid):
    '''
    Checks if a player is ghosting and blinds them if so (does not test bots)
    '''
    if not es.isbot(uid):
        plist = es.createplayerlist()
        uip = plist[uid]["address"]   
        for id in plist:
            testip = plist[id]["address"]
            if testip == uip:
                blindplayer(uid) 

def load():
    global ipg_active
    global text
    global ghosting
    # Register the module
    ghosting = xa.register("xaipghosting") 
    # Get the (mani) variable, if manimode is OFF it defaults to 1 (or on). 
    ipg_active = xa.setting.createVariable(ghosting, 'blind_ghosters', '1', "XA: Blind IP Ghosters when they die (1=On, 0=Off)") 
    # Grab the languages file using the XA langlib wrapper
    text = xa.language.getLanguage('xaipghosting')
    xa.logging.log(ghosting, "Loaded IP Ghosting (mani clone) V1.0")

def player_death(event_var):
    global blinded
    '''
    If player is IP ghosting add them to the list! And if the repeat is not fired yet then do that too!
    '''
    if xa.setting.getVariable(ghosting, 'blind_ghosters') != "0":
        checkplayer(event_var['userid'])

def round_end(event_var):
    '''
    On the round end delete the keys from our dict of ghosters and also end the repeat to minimize server load
    '''
    global blinded
    if repeat.status("xaip") > 0:
        r = repeat.find("xaip")
        r.stop()
    blinded = {}

def unload():
    xa.logging.log(mymodule, "XA module xaipghosting is being unloaded.")
    # Unregister the module
    xa.unregister("xaipghosting")