import es
import playerlib
from es import server_var
from keymenu import keymenu
import keyvalues

info = es.AddonInfo()
info.name = "XA: Skins"
info.version = "0.21"
info.author = "Don"
info.url = "Http://forums.mattie.info"
info.description = "Clone of Mani skins feature for XA"
info.tags = "skins models XA"

skinmenu = ['Admin T', 'Admin CT', 'Public T', 'Public CT', 'Reserved T', 'Reserved CT', 'Misc']
skinnames = ['admin_t', 'admin_ct', 'public_t', 'public_ct', 'reserved_t', 'reserved_ct', 'misc']
playerid = 0
skins_downloadable = 1
xaskins_path = server_var['eventscripts_gamedir'] + "/addons/eventscripts/xaskins/"
xaskins_skinfiles_path = server_var['eventscripts_gamedir'] + "/cfg/mani_admin_plugin/skins/"

def load():
# This function is called when the script is es_load-ed
    es.keygroupcreate("xaskins_player_settings")
    x = es.keygroupgetpointer("xaskins_player_settings")
    es.keyploadfromfile(x, xaskins_path + "es_xaskins_player_settings_db.txt")
    if not es.exists("command", "xaskin"):
        es.regcmd("xaskin", "xaskins/consolecmd", "Skins console command")
        es.regclientcmd("xaskin", "xaskins/consolecmd", "Skins console command")
    for i in range(7):
        add_skin_files(skinnames, i)

def unload():
# This function is called when the script is es_unload-ed
    x = es.keygroupgetpointer("xaskins_player_settings")
    es.keypsavetofile(x, xaskins_path + "es_xaskins_player_settings_db.txt")
    es.keygroupdelete("xaskins_player_settings")
    for i in range(7):
        es.keygroupdelete(skinnames[i] + "skin")
        
def es_player_validated(event_var):
# This function is called when a player is validated
# Check if the player is in the database yet
    player_exists = es.exists("key", "xaskins_player_settings", event_var['networkid'])
# If not in the database then go create a record
    if player_exists == 0:
        create_record(event_var['networkid'])
        
def player_spawn(event_var):
# This function is called when a player spawns.  It gets the player's current level
# then gets the team and then the model and sets it
    if event_var['es_steamid'] != "BOT":
        if event_var['es_userteam'] == "2" or event_var['es_userteam'] == "3":
            level = es.keygetvalue("xaskins_player_settings", event_var['es_steamid'], "level")[0]
            level = level.lower()
            if event_var['es_userteam'] == "2":
                team = 't'
            elif event_var['es_userteam'] == "3":
                team = 'ct'
            model = es.keygetvalue("xaskins_player_settings", event_var['es_steamid'], level + team + "m")
            if model != "None":
                myPlayer = playerlib.getPlayer(event_var['userid'])
                myPlayer.set('model', model)

def create_record(steamid):
# This function creates a new player record
    es.keycreate("xaskins_player_settings", steamid)
    es.keysetvalue("xaskins_player_settings", steamid, "level", "Public")
    es.keysetvalue("xaskins_player_settings", steamid, "Admin T", "None")
    es.keysetvalue("xaskins_player_settings", steamid, "atm", "None")
    es.keysetvalue("xaskins_player_settings", steamid, "Admin CT", "None")
    es.keysetvalue("xaskins_player_settings", steamid, "actm", "None")
    es.keysetvalue("xaskins_player_settings", steamid, "Public T", "None")
    es.keysetvalue("xaskins_player_settings", steamid, "ptm", "None")
    es.keysetvalue("xaskins_player_settings", steamid, "Public CT", "None")
    es.keysetvalue("xaskins_player_settings", steamid, "pctm", "None")
    es.keysetvalue("xaskins_player_settings", steamid, "Reserved T", "None")
    es.keysetvalue("xaskins_player_settings", steamid, "rtm", "None")
    es.keysetvalue("xaskins_player_settings", steamid, "Reserved CT", "None")
    es.keysetvalue("xaskins_player_settings", steamid, "rctm", "None")
    x = es.keygroupgetpointer("xaskins_player_settings")
    es.keypsavetofile(x, xaskins_path + "es_xaskins_player_settings_db.txt")

def consolecmd():
# This function handles the console and client command.  Probably need to modify for use with XA
    argc = es.getargc()
    playerid = es.getcmduserid()
    mysteamid = es.getplayersteamid(playerid)
    if argc == 1:
        es.keygroupcreate("xaskins")
        j = 0
        for i in skinmenu:
            if i != "Misc":
                myskin = es.keygetvalue("xaskins_player_settings", mysteamid, i)
                es.keycreate("xaskins", i + " - " + myskin)
                es.keysetvalue("xaskins", i + " - " + myskin, "skinmenu", skinnames[j])
            j+=1
        a = keymenu.create("xaskinmenu", "_keymenu_select", "xaskins/selectmenu", "xaskins", "#key", "#keyvalue skinmenu", "Skinlist\nSelect a Skin Menu")
        a.send(playerid)
        es.keygroupdelete("xaskins")

def selectmenu():
# This function makes the submenu for whichever set of skins was chosen
    es.keycreate('xaskinuser' + server_var['_popup_userid'])
    es.keysetvalue('xaskinuser' + server_var['_popup_userid'], 'skinset', server_var['_keymenu_select'])
    a = keymenu.create("xaskinmenu", "_keymenu_select", "xaskins/selectsubmenu", server_var['_keymenu_select'] + "skin", "#key", "#key", "Select a Skin Color")
    a.send(server_var['_popup_userid'])

def selectsubmenu():
# In this function we need to set the model path into the player's settings
    levelset = es.keygetvalue('xaskinuser' + server_var['_popup_userid'], 'skinset')
    mykey = levelset + 'skin'
    mynewskin = es.keygetvalue(mykey, server_var['_keymenu_select'], 'skin')
    mysteamid = es.getplayersteamid(server_var['_popup_userid'])
    if levelset == "admin_t":
        es.keysetvalue("xaskins_player_settings", mysteamid, "Admin T", server_var['_keymenu_select'])
        es.keysetvalue("xaskins_player_settings", mysteamid, "atm", mynewskin)
    elif levelset == "admin_ct":
        es.keysetvalue("xaskins_player_settings", mysteamid, "Admin CT", server_var['_keymenu_select'])
        es.keysetvalue("xaskins_player_settings", mysteamid, "actm", mynewskin)
    elif levelset == "reserved_t":
        es.keysetvalue("xaskins_player_settings", mysteamid, "Reserved T", server_var['_keymenu_select'])
        es.keysetvalue("xaskins_player_settings", mysteamid, "rtm", mynewskin)
    elif levelset == "reserved_ct":
        es.keysetvalue("xaskins_player_settings", mysteamid, "Reserved CT", server_var['_keymenu_select'])
        es.keysetvalue("xaskins_player_settings", mysteamid, "rctm", mynewskin)
    elif levelset == "public_t":
        es.keysetvalue("xaskins_player_settings", mysteamid, "Public T", server_var['_keymenu_select'])
        es.keysetvalue("xaskins_player_settings", mysteamid, "ptm", mynewskin)
    elif levelset == "public_ct":
        es.keysetvalue("xaskins_player_settings", mysteamid, "Public CT", server_var['_keymenu_select'])
        es.keysetvalue("xaskins_player_settings", mysteamid, "pctm", mynewskin)
    es.keydelete('xaskinuser' + server_var['_popup_userid'])
    x = es.keygroupgetpointer("xaskins_player_settings")
    es.keypsavetofile(x, xaskins_path + "es_xaskins_player_settings_db.txt")
    
def add_skin_files(skin, i):
# This function reads in the 7 main skin files and parses each one
    fp = open(xaskins_skinfiles_path + skin[i] +".txt")
    es.keygroupcreate(skin[i] + "skin")
    for line in fp:
        line = line.strip("\n")
        line = line.strip("\r")
        if line[0:1] == '"':
            skinfile = line[findsplit(line)+1:len(line)]
            skinname = line[0:findsplit(line)]
            skinname = skinname.strip('"')
            skinmodel = makedownloadable(skinfile,skin[i])
            es.keycreate(skin[i] + "skin", skinname)
            es.keysetvalue(skin[i] + "skin", skinname, 'skin', skinmodel)
            
def makedownloadable(skinfile,skingroup):
# This function reads each model/material list files and makes them downloadable if cvar set.  Also returns model name
    sp =open(xaskins_skinfiles_path + skingroup + "/" + skinfile)
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
