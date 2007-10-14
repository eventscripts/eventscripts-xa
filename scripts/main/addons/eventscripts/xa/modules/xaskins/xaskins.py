import es
from es import server_var
import xa
import xa.language
import xa.logging
import xa.setting
import xa.playerdata
from xa.modules.xasettings import xasettings
from xa import xa
import services
import playerlib

info = es.AddonInfo()
info.name           = "XA: Skins"
info.version        = "0.23"
info.author         = "Don"
info.url            = "http://forums.mattie.info/"
info.description    = "Clone of Mani skins feature for XA"
info.tags           = "skins models XA"

skinmenu                = ['Admin T', 'Admin CT', 'Public T', 'Public CT', 'Reserved T', 'Reserved CT', 'Misc']
skinnames               = ['admin_t', 'admin_ct', 'public_t', 'public_ct', 'reserved_t', 'reserved_ct', 'misc']
skinlist                = {}
playerid                = 0
playermenu              = {}
skins_downloadable      = 1
xaskins_path            = server_var['eventscripts_gamedir'] + "/addons/eventscripts/xaskins/"
xaskins_skinfiles_path  = server_var['eventscripts_gamedir'] + "/cfg/mani_admin_plugin/skins/"

# Register XASkins as a xa module
xaskins                 = xa.register('xaskins')
xaskins.addRequirement('xasettings')
# Load strings.ini from the module folder
xalanguage              = xa.language.getLanguage(xaskins)
# Register the settings
xaplayerdata_exists         = xa.playerdata.createUserSetting(xaskins, "exists")
xaplayerdata_admin_t        = xa.playerdata.createUserSetting(xaskins, "admin_t")
xaplayerdata_admin_ct       = xa.playerdata.createUserSetting(xaskins, "admin_ct")
xaplayerdata_reserved_t     = xa.playerdata.createUserSetting(xaskins, "reserved_t")
xaplayerdata_reserved_ct    = xa.playerdata.createUserSetting(xaskins, "reserved_ct")
xaplayerdata_public_t       = xa.playerdata.createUserSetting(xaskins, "public_t")
xaplayerdata_public_ct      = xa.playerdata.createUserSetting(xaskins, "public_ct")

xaplayerdata_admin_t_skin        = xa.playerdata.createUserSetting(xaskins, "admin_t_skin")
xaplayerdata_admin_ct_skin       = xa.playerdata.createUserSetting(xaskins, "admin_ct_skin")
xaplayerdata_reserved_t_skin     = xa.playerdata.createUserSetting(xaskins, "reserved_t_skin")
xaplayerdata_reserved_ct_skin    = xa.playerdata.createUserSetting(xaskins, "reserved_ct_skin")
xaplayerdata_public_t_skin       = xa.playerdata.createUserSetting(xaskins, "public_t_skin")
xaplayerdata_public_ct_skin      = xa.playerdata.createUserSetting(xaskins, "public_ct_skin")

def load():
# This function is called when the script is es_load-ed
    # Register client console and server command
    xaskincommand = xaskins.addCommand("xaskin", consolecmd, "set_skin", "#all")
    xaskincommand.register(['console', 'server'])
    xasettings.registerMethod(xaskins, consolecmd, xalanguage["player skins"])
    for i in range(7):
        add_skin_files(i)

def unload():
# This function is called when the script is es_unload-ed
    xaskins.unRegister()
        
def player_activate(event_var):
# This function is called when a player is validated
# Check if the player is in the database yet
    player_exists = xaplayerdata_exists.exists(int(event_var['userid']))
# If not in the database then go create a record
    if not player_exists:
        create_record(int(event_var['userid']))
        
def player_spawn(event_var):
# This function is called when a player spawns.  It gets the player's current level
# then gets the team and then the model and sets it
    if event_var['es_steamid'] != "BOT":
        if event_var['es_userteam'] == "2" or event_var['es_userteam'] == "3":
            auth = services.use("auth")
            if auth.isUseridAuthorized(int(event_var['userid']), "skin_admin"):
                level = "admin"
            elif auth.isUseridAuthorized(int(event_var['userid']), "skin_reserved"):
                level = "reserved"
            else:
                level = "public"
            if event_var['es_userteam'] == "2":
                team = 't'
            elif event_var['es_userteam'] == "3":
                team = 'ct'
            xaplayerdata = xa.playerdata.getUserSetting(xaskins, level + '_' + team + '_skin')
            model = xaplayerdata.get(int(event_var['userid']))
            print model, level + '_' + team + '_skin'
            if model != "":
                myPlayer = playerlib.getPlayer(event_var['userid'])
                myPlayer.set('model', model)

def create_record(userid):
# This function creates a new player record
    xaplayerdata_exists.set(userid, "1")
    xaplayerdata_admin_t.set(userid, "None")
    xaplayerdata_admin_ct.set(userid, "None")
    xaplayerdata_reserved_t.set(userid, "None")
    xaplayerdata_reserved_ct.set(userid, "None")
    xaplayerdata_public_t.set(userid, "None")
    xaplayerdata_public_ct.set(userid, "None")
    
    xaplayerdata_admin_t_skin.set(userid, "")
    xaplayerdata_admin_ct_skin.set(userid, "")
    xaplayerdata_reserved_t_skin.set(userid, "")
    xaplayerdata_reserved_ct_skin.set(userid, "")
    xaplayerdata_public_t_skin.set(userid, "")
    xaplayerdata_public_ct_skin.set(userid, "")
    
    xa.playerdata.saveKeyValues()
    
def consolecmd(playerid = False):
# This function handles the console and client command.  Probably need to modify for use with XA
    if not playerid:
        playerid = es.getcmduserid()
    page = popuplib.easymenu("xaskinmenu"+str(playerid), "_tempcore", _selectmenu)
    page.cachemode = "user"
    page.settitle(xalanguage["choose skins"])
    j = 0
    for i in skinmenu:
        if i != "Misc":
            xaplayerdata = xa.playerdata.getUserSetting(xaskins, skinnames[j])
            myskin = xaplayerdata.get(playerid)
            page.addoption(skinnames[j], i + " - " + myskin)
            
        j+=1
    page.send(playerid)

def _selectmenu(userid, choice, name):
# This function makes the submenu for whichever set of skins was chosen
    playermenu[userid] = choice
    page = popuplib.easymenu("xaskinselect"+str(playerid), "_tempcore", _selectsubmenu)
    page.cachemode = "user"
    page.settitle(xalanguage["choose skins"])
    for i in skinlist[choice]:
        page.addoption(i, i)
    page.send(playerid)

def _selectsubmenu(userid, choice, name):
# In this function we need to set the model path into the player's settings
    levelset = playermenu[userid]
    mynewskin = skinlist[levelset][choice]
    if levelset == "admin_t":
        xaplayerdata_admin_t.set(userid, choice)
        xaplayerdata_admin_t_skin.set(userid, mynewskin)
    elif levelset == "admin_ct":
        xaplayerdata_admin_ct.set(userid, choice)
        xaplayerdata_admin_ct_skin.set(userid, mynewskin)
    elif levelset == "reserved_t":
        xaplayerdata_reserved_t.set(userid, choice)
        xaplayerdata_reserved_t_skin.set(userid, mynewskin)
    elif levelset == "reserved_ct":
        xaplayerdata_reserved_ct.set(userid, choice)
        xaplayerdata_reserved_ct_skin.set(userid, mynewskin)
    elif levelset == "public_t":
        xaplayerdata_public_t.set(userid, choice)
        xaplayerdata_public_t_skin.set(userid, mynewskin)
    elif levelset == "public_ct":
        xaplayerdata_public_ct.set(userid, choice)
        xaplayerdata_public_ct_skin.set(userid, mynewskin)
    xa.playerdata.saveKeyValues()
    
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
                return line
            
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
