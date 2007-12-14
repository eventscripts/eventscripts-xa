import es
import xa
import xa.language
import xa.logging
import xa.playerdata
import xa.setting
import services
from xa import xa
import playerlib
import os

#plugin information
info = es.AddonInfo()
info.name = "XA:Reserve Slots"
info.version = "1.0a"
info.author = "Errant"
info.url = ""
info.description = "Clone of Mani's reserve slot feature for XA"
info.tags = "admin reserve slots kick players XA"


'''
XA:Reserved slots - a full port of manis reserved slots (horrible though it is Smile) functionality for eXtendable Admin.
This module uses all the Mani configuration straight from the box.
However currently this feature does NOT support the redirect option. IF a server IP is set this is added to the kick message.
'''


def returnUnreserved(x):
    if mani_reservedlist:
        # if we have a list of reserved players then check x's steam id and return false if they are in the list
        if x.attributes['steamid'] in mani_reservedlist:
            return False
    if mani_admin_reservedlist:
        # if we have a list of reserved players then check x's steam id and return false if they are in the list
        if x.attributes['steamid'] in mani_admin_reservedlist:
            return False
    if xa_reservedlist:
        # if we have a list of reserved players then check x's steam id and return false if they are in the list
        if x.attributes['steamid'] in xa_reservedlist:
            return False
    if xa.isManiMode():
        # if we have mani mode on we can test for the "N" immunity for reserve slot kick immunity
        if auth.isUseridAuthorized(int(x), "n", "immunity"):
            return False
    # and finally check that they are not on the reserved list
    if auth.isUseridAuthorized(int(x), "reserve_slot"):
        return False
    return True

def load_reserved(file):
    res_path = os.getcwd() + "/cstrike/cfg/" + file
    if os.path.exists(res_path):
        fp = open(res_path)
        temp = []
        for line in fp:
            line = line.strip("\n")
            line = line.strip("\r")
            if line.startswith("STEAM"):
                safesplit = line.split(" ")
                temp.append(safesplit[0])
        return temp
    else:
        return False


def load():
    global rslots, text, mani_reservedlist, xa_reservedlist, auth
    #rslots = reservedSlots()
    # Register the module
    rslots = xa.register("xareserveslots")
    # run the configuration variables
    cfg_vars()
    # grab the list of reserved players
    if xa.isManiMode():
        # woot manit mode is on so lets check the mani file
        mani_reservedlist = load_reserved("mani_admin_plugin/reserveslots.txt")
    xa_reservedlist = load_reserved("xa/xareserveslots/reserved_slots_list.txt")
    # Get the lang file
    text = xa.language.getLanguage('xareserveslots')
    # register the playerlib player filter we have..
    playerlib.registerPlayerListFilter("#res", returnUnreserved)
    # load the auth service
    auth = services.use("auth")
    # register the capapbility
    auth.registerCapability("reserve_slot", auth.ADMIN)
    # And say were loaded!
    es.dbgmsg(1, "Loaded Reserve slots (mani clone) V1.0")
 
def unload():
    xa.unregister("xareserveslots")
   
def es_map_start(event_var):
    global mani_reservedlist, xa_reservedlist
    if xa.isManiMode():
        # woot manit mode is on so lets check the mani file
        mani_reservedlist = load_reserved("mani_admin_plugin/reserveslots.txt")
        mani_admin_reservedlist = load_reserved("mani_admin_plugin/adminlist.old.txt")
    xa_reservedlist = load_reserved("xa/xareserveslots/reserved_slots_list.txt")
       
def cfg_vars():
    vars = {
    "reserve_slots":{"val":"1", "desc":"XA: Turn on reserve slots (1=On, 0=Off)"},
    "reserve_slots_kick_method":{"val":"0", "desc":"XA: Reserve slots kick selection (1=By time connected, 0=By ping)"},
    "reserve_slots_redirect":{"val":"0", "desc":"XA: Redirect people without reserved slots to an IP (will not redirect them but will give them the IP on kick"},
    "reserve_slots_kick_message":{"val":"0", "desc":"XA: A message to give to people when you kick them for using a reserved slot [0=use the ES language file]"},
    "reserve_slots_number_of_slots":{"val":"0", "desc":"XA: The number of reserved slots on the server"},
    "reserve_slots_allow_slot_fill":{"val":"0", "desc":"XA: Allow reserved slots to fill on the server [0=do not let them fill, 1=allow them to fill]"},
    }
    for x in vars:
        xa.setting.createVariable("xareserveslots", x, vars[x]["val"], vars[x]["desc"])
    # now if we have no mani mode on then let's update these variables with our own settings
    if not xa.isManiMode():
        if os.path.exists("/addons/eventscripts/cfg/xa/xareserveslots/xareserveslots.cfg"):
            es.server.cmd('es_xmexec ../addons/eventscripts/cfg/xa/xareserveslots.cfg')
        else:
            es.dbgmsg(0, "XA Reserve Slosts: The main cfg file could not be loaded.")


def player_activate(event_var):
    if xa.setting.getVariable("xareserveslots", "reserve_slots"):
        check_player(event_var["userid"])

def check_player(userid):
    maxplayers = es.getmaxplayercount()
    pdiff = maxplayers - es.getplayercount()
    if pdiff <= int(xa.setting.getVariable("xareserveslots", "reserve_slots_number_of_slots")):
        # ok so there we are into the reserved slots...
        if returnUnreserved(userid):
            # The player is NOT allowed in a reserved slot so we kick them
            kickPlayer(playerlib.getPlayer(userid) )
        else:
            # they are on the res list - so kick someone else??
            if int(xa.setting.getVariable("xareserveslots", "reserve_slots_allow_slot_fill")) == 0:
                #  we are not allowing the slots to fill so lets kick someone
                uid = chooseKick()
                kickPlayer(uid)
               
def kickPlayer(ulib):
    ip = str(xa.setting.getVariable("xareserveslots", "reserve_slots_redirect"))
    if ip != "0":
        # we have an ip to get!
        es.dbgmsg(0, "TODO: Reserved slots doesn't yet support redirect. %s" % ip)
    else:
        if str(xa.setting.getVariable("xareserveslots", "reserve_slots_kick_message")) != "0":
            if ip != "0":
                msg = text("ip_kick_message",{"ip":ip},ulib.get("lang"))
            else:
                msg = text("kick_message",None,ulib.get("lang"))
        else:
            if ip != "0":
                msg = str(xa.setting.getVariable("xareserveslots", "reserve_slots_kick_message"))
            else:
                msg = str(xa.setting.getVariable("xareserveslots", "reserve_slots_kick_message")) + " " + ip
        ulib.kick(msg)
   
def chooseKick():
    '''
    Chooses someone to kick, in the following order:
    1) Bots
    2) Either via Ping or by time (according to mani cfg)
    '''
    botlist = playerlib.getPlayerList("#bot")
    if len(botlist) == 1:   
        # we have to be careful here because of srcTV being in the bot list
        if botlist[0].attributes["steamid"] == "BOT":
            botlist[0]
        else:
            # aha it was  a srcTV....
            return ChoosePlayer()
    elif len(botlist) == 0:
        # just human players.. so
        return choosePlayer()
    else:
        # we have bots! so kick one
        for bot in botlist:
            if bot.attributes["steamid"] == "BOT":
                return bot
           
def choosePlayer():         
    '''
    Used by chooseKick() to determine a player to kick
    '''
    kicklist = playerlib.getPlayerList("#res")
    if int(xa.setting.getVariable("xareserveslots", "reserve_slots_kick_method")) == 1:
        timelowest = 1000000000000
        for id in kicklist:
            time = id.attributes["timeconnected"]   
            if time < timelow:
                timelowest = time
                kickuid = id
        return kickuid
    else:
        ping = 0
        for id in kicklist:
            pping = id.attributes["ping"]
            if pping > ping:
                ping = pping
                kickuid = id
        return kickuid
        
