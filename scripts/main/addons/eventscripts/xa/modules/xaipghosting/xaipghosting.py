# es imports
import es
import playerlib
import repeat
import usermsg
# xa imports
import xa
import xa.language
import xa.logging
import xa.setting
from xa import xa 

#plugin information
info = es.AddonInfo()
info.name = "XA:IP Ghosting"
info.version = "1.1.0"
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
1.1.0 | [FULL] | 21/01/2008 | Changed to using a class for the blind, fixed a few idiot errors and cleaned things up a bit. Added a cvar to show the version publicly. Added logging of the blind


--Future--
 #  |  Status       | Desc
1.5 | [UNSTARTED]   | Add other features, provide admin notification / features, add further config options
'''

# the dictionary to track blinded players
blinded = {}

# Grab the languages file using the XA langlib wrapper
text = xa.language.getLanguage('xaipghosting')

# Public variable for version
es.ServerVar("xa_blind_ip_ghosters_ver" info.version, "XA: Blind IP Ghosters, version").makepublic()

'''
Internal classes
'''
class Player(playerlib.Player)
    '''
    Extends playerlib.Player to provide special functions
    '''
    def blind(self):
        '''
        The actual blind
        '''
        usermsg.fade(self.id,2,500,1000,0,0,0,255)
    def tell_blinded(self):
        '''
        Used to tell the player they were blinded
        '''
        # And tell them about it
        es.tell(int(self.id), text("blind_message",None,self.get("lang")))
        es.tell(int(self.id), text("blind_message",None,self.get("lang")))
        es.tell(int(self.id), text("blind_message",None,self.get("lang")))
        
'''
Internal methods
'''
def repeat_fade(x):
    '''
    Method to handle the fading. Is run every second by the repeat xaip. 
    The fade is set to fade out so on round end you get a nice fade out effect for the player
    '''
    for uid in blinded:
        blinded[uid].blind()


def blindplayer(uid)
    '''
    - Starts the fade repeat if it isn't already running
    - Fades out the player
    - Tell them 3 times they have been blinded
    '''
    global blinded
    if repeat.status("xaip") == 0:
        a = repeat.create("xaip", repeat_fade)
        a.start(1,0)
    # do the initial fade 
    blinded[uid] = Player(uid)
    blinded[uid].blind()
    # tell them
    blinded[uid].tell_blinded()
    # log that they were blinded
    xa.logging.log(ghosting, "Blinded player %s (%s)" % (str(uid), es.getsteamid(uid)))
    

def checkplayer(uid):
    '''
    Checks if a player is ghosting and blinds them if so (does not test bots)
    '''
    if not es.isbot(uid):
        plist = es.createplayerlist()
        uip = plist[int(uid)]["address"]   
        for id in plist:
            testip = plist[id]["address"]
            if testip == uip:
                blindplayer(uid) 
'''
Events
'''
def load():
    global ghosting
    # Register the module
    ghosting = xa.register("xaipghosting") 
    # sort the variable registration
    xa.setting.createVariable(ghosting, 'blind_ghosters', '1', "XA: Blind IP Ghosters when they die (1=On, 0=Off)") 
    # log what happened
    xa.logging.log(ghosting, "Loaded IP Ghosting (mani clone) V%s" % (info.version))

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
    xa.logging.log(ghosting, "XA module xaipghosting is being unloaded.")
    # Unregister the module
    xa.unregister("xaipghosting")