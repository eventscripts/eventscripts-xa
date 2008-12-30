import es
import os
import popuplib
import playerlib
from xa import xa

info = es.AddonInfo()
info.name           = "Skins"
info.version        = "0.44"
info.author         = "Don"
info.url            = "http://forums.mattie.info"
info.description    = "Skins feature for XA"
info.tags           = "skins models XA"

skinmenu                = ['Admin T', 'Admin CT', 'Public T', 'Public CT', 'Reserved T', 'Reserved CT', 'Misc']
skinnames               = ['admin_t', 'admin_ct', 'public_t', 'public_ct', 'reserved_t', 'reserved_ct', 'misc']
skinlist                = {}
playermenu              = {}
skins_downloadable      = 1
if xa.isManiMode():
    xaskins_skinfiles_path  = xa.gamedir() + "/cfg/mani_admin_plugin/skins/"
else:
    xaskins_skinfiles_path  = xa.gamedir() + "/cfg/xa/skins/"

# Register XASkins as a xa module
xaskins                 = xa.register('xaskins')
# Load strings.ini from the module folder
xalanguage              = xaskins.language.getLanguage()
# Register the settings
xaplayerdata_exists         = xaskins.playerdata.createUserSetting("exists")
xaplayerdata_admin_t        = xaskins.playerdata.createUserSetting("admin_t")
xaplayerdata_admin_ct       = xaskins.playerdata.createUserSetting("admin_ct")
xaplayerdata_reserved_t     = xaskins.playerdata.createUserSetting("reserved_t")
xaplayerdata_reserved_ct    = xaskins.playerdata.createUserSetting("reserved_ct")
xaplayerdata_public_t       = xaskins.playerdata.createUserSetting("public_t")
xaplayerdata_public_ct      = xaskins.playerdata.createUserSetting("public_ct")

xaplayerdata_admin_t_skin        = xaskins.playerdata.createUserSetting("admin_t_skin")
xaplayerdata_admin_ct_skin       = xaskins.playerdata.createUserSetting("admin_ct_skin")
xaplayerdata_reserved_t_skin     = xaskins.playerdata.createUserSetting("reserved_t_skin")
xaplayerdata_reserved_ct_skin    = xaskins.playerdata.createUserSetting("reserved_ct_skin")
xaplayerdata_public_t_skin       = xaskins.playerdata.createUserSetting("public_t_skin")
xaplayerdata_public_ct_skin      = xaskins.playerdata.createUserSetting("public_ct_skin")

def load():
# This function is called when the script is es_load-ed
    # Register client console and server command
    xaskins.registerCapability("skin_admin", "ADMIN")
    xaskins.registerCapability("skin_reserved", "POWERUSER")
    xaskincommand = xaskins.addCommand("xaskin", _sendmenu, "set_skin", "UNRESTRICTED")
    xaskincommand.register(['console', 'server'])
    xaskins.addRequirement('xasettings')
    xaskins.xasettings.registerMethod("xaskins", _sendmenu, xalanguage["player skins"])
    check_if_files_exist()
    if str(es.ServerVar('eventscripts_currentmap')) != "": es_map_start(None)

def unload():
# This function is called when the script is es_unload-ed
    xaskins.xasettings.unregister("xaskins")
    xaskins.delRequirement("xasettings")
    xaskins.unregister()

def es_map_start(event_var):
    for i in range(7):
        add_skin_files(i)

def player_activate(event_var):
# This function is called when a player is validated
# Check if the player is in the database yet
# If not in the database then go create a record
    create_record(event_var)
        
def player_spawn(event_var):
# This function is called when a player spawns.  It gets the player's current level
# Check if the player is in the database yet
# If not in the database then go create a record
    create_record(event_var)
# then gets the team and then the model and sets it
    if event_var['es_steamid'] != "BOT":
        if event_var['es_userteam'] == "2" or event_var['es_userteam'] == "3":
            if xaskins.isUseridAuthorized(int(event_var['userid']), "skin_admin"):
                level = "admin"
            elif xaskins.isUseridAuthorized(int(event_var['userid']), "skin_reserved"):
                level = "reserved"
            else:
                level = "public"
            if event_var['es_userteam'] == "2":
                team = 't'
            elif event_var['es_userteam'] == "3":
                team = 'ct'
            xaplayerdata_skin = xaskins.playerdata.getUserSetting(level + '_' + team + '_skin')
            model = xaplayerdata_skin.get(int(event_var['userid']))
            if model != "None" and model != None:
                myPlayer = playerlib.getPlayer(event_var['userid'])
                myPlayer.set('model', model)
                
def create_record(event_var):
    userid = int(event_var['userid'])
    if not xaplayerdata_exists.exists(userid):
        xaplayerdata_exists.set(userid, "1")
        xaplayerdata_admin_t.set(userid, "None")
        xaplayerdata_admin_ct.set(userid, "None")
        xaplayerdata_reserved_t.set(userid, "None")
        xaplayerdata_reserved_ct.set(userid, "None")
        xaplayerdata_public_t.set(userid, "None")
        xaplayerdata_public_ct.set(userid, "None")
        xaplayerdata_admin_t_skin.set(userid, "None")
        xaplayerdata_admin_ct_skin.set(userid, "None")
        xaplayerdata_reserved_t_skin.set(userid, "None")
        xaplayerdata_reserved_ct_skin.set(userid, "None")
        xaplayerdata_public_t_skin.set(userid, "None")
        xaplayerdata_public_ct_skin.set(userid, "None")
        xaskins.playerdata.saveKeyValues()
    
def _sendmenu(playerid = False):
# This function handles the console and client command.  Probably need to modify for use with XA
    if not playerid:
        playerid = es.getcmduserid()
    if popuplib.exists("xaskinmenu"+str(playerid)):
        popuplib.delete("xaskinmenu"+str(playerid))
    page = popuplib.easymenu("xaskinmenu"+str(playerid), "_tempcore", _selectmenu)
# This is commented out becuase popuplib seems to have a bug
#    page.cachemode = "user"
    page.settitle(xalanguage["choose skins"])
    j = 0
    for i in skinmenu:
        if (i != "Misc") and ((xaskins.isUseridAuthorized(playerid, "skin_admin") and ("admin" == skinnames[j][0:5])) or (xaskins.isUseridAuthorized(playerid, "skin_reserved") and ("reserved" == skinnames[j][0:8])) or ("public" == skinnames[j][0:6])):
            xaplayerdata = xaskins.playerdata.getUserSetting(skinnames[j])
            myskin = xaplayerdata.get(playerid)
            page.addoption(skinnames[j], i + " - " + myskin)
        j+=1
    page.send(playerid)

def _selectmenu(userid, choice, name):
# This function makes the submenu for whichever set of skins was chosen
    playermenu[userid] = choice
    if popuplib.exists("xaskinselect"+str(userid)):
        popuplib.delete("xaskinselect"+str(userid))
    page = popuplib.easymenu("xaskinselect"+str(userid), "_tempcore", _selectsubmenu)
# This is commented out becuase popuplib seems to have a bug
#    page.cachemode = "user"
    page.settitle(xalanguage["choose skins"])
    for i in skinlist[choice]:
        page.addoption(i, i)
    page.send(userid)

def _selectsubmenu(userid, choice, name):
# In this function we need to set the model path into the player's settings
    levelset = playermenu[userid]
    mynewskin = skinlist[levelset][choice]
    xaplayerdata = xaskins.playerdata.getUserSetting(levelset)
    xaplayerdata_skin = xaskins.playerdata.getUserSetting(levelset + '_skin')
    xaplayerdata.set(userid, choice)
    xaplayerdata_skin.set(userid, mynewskin)
    xaskins.playerdata.saveKeyValues()
    
def add_skin_files(i):
# This function reads in the 7 main skin files and parses each one
    skinlist[skinnames[i]] = {}
    fp = open(xaskins_skinfiles_path + skinnames[i] +".txt")
    for line in fp:
        line = line.strip("\n")
        line = line.strip("\r")
        if line[0:1] == '"':
            skinfile = line[findsplit(line)+1:len(line)]
            skinname = line[0:findsplit(line)]
            skinname = skinname.strip('"')
            skinmodel = makedownloadable(skinfile,skinnames[i])
            skinlist[skinnames[i]][skinname] = skinmodel
            
def makedownloadable(skinfile,skingroup):
# This function reads each model/material list files and makes them downloadable if cvar set.  Also returns model name
    sp = open(xaskins_skinfiles_path + skingroup + "/" + skinfile)
    for line in sp:
        line = line.strip("\n")
        line = line.strip("\r")
        if line[0:2] != '//' and line != '':
            if skins_downloadable == 1:
                es.stringtable("downloadables", line)
            if '.mdl' in line:
                model = line
    return model
            
def findsplit(phrase):
# This function just splits the lines in the main skin files and returns the line position of the split
    foundsplit = 0
    linelen = len(phrase)
    i = linelen - 1
    while i > 1 and foundsplit == 0:
        if phrase[i] == ' ':
            split = i
            foundsplit = 1
            return i
        i-=1

def check_if_files_exist():
    if not os.path.isdir(xa.gamedir() + "/cfg/xa"):
        os.mkdir(xa.gamedir() + "/cfg/xa")
    if not os.path.isdir(xaskins_skinfiles_path):
        os.mkdir(xaskins_skinfiles_path)
    if not os.path.isfile(xaskins_skinfiles_path + 'admin_t.txt'):
        print "does not exist"
        f = open(xaskins_skinfiles_path + 'admin_t.txt', 'w')
        f.close()
    if not os.path.isfile(xaskins_skinfiles_path + 'admin_ct.txt'):
        f = open(xaskins_skinfiles_path + 'admin_ct.txt', 'w')
        f.close()
    if not os.path.isfile(xaskins_skinfiles_path + 'reserved_t.txt'):
        f = open(xaskins_skinfiles_path + 'reserved_t.txt', 'w')
        f.close()
    if not os.path.isfile(xaskins_skinfiles_path + 'reserved_ct.txt'):
        f = open(xaskins_skinfiles_path + 'reserved_ct.txt', 'w')
        f.close()
    if not os.path.isfile(xaskins_skinfiles_path + 'public_t.txt'):
        f = open(xaskins_skinfiles_path + 'public_t.txt', 'w')
        f.close()
    if not os.path.isfile(xaskins_skinfiles_path + 'public_ct.txt'):
        f = open(xaskins_skinfiles_path + 'public_ct.txt', 'w')
        f.close()
    if not os.path.isfile(xaskins_skinfiles_path + 'misc.txt'):
        f = open(xaskins_skinfiles_path + 'misc.txt', 'w')
        f.close()
