import es
import playerlib
from es import server_var
from keymenu import keymenu

info = es.AddonInfo()
info.name = "XA: Skins"
info.version = "0.12"
info.author = "Don"
info.url = "Http://forums.mattie.info"
info.description = "Clone of Mani skins feature for XA"
info.tags = "skins models XA"

skinmenu = ['Admin CT', 'Admin T', 'Public CT', 'Public T', 'Reserved CT', 'Reserved T', 'Misc']
skinnames = ['admin_ct', 'admin_t', 'public_ct', 'public_t', 'reserved_ct', 'reserved_t', 'misc']
playerid = 0
skins_downloadable = 1

def load():
# This function is called when the script is es_load-ed
    if not es.exists("command", "xaskin"):
        es.regcmd("xaskin", "xaskins/consolecmd", "Skins console command")
        es.regclientcmd("xaskin", "xaskins/consolecmd", "Skins console command")
    for i in range(7):
        add_skin_files(skinnames, i)

def unload():
# This function is called when the script is es_unload-ed
    for i in range(7):
        es.keygroupdelete(skinnames[i] + "skin")


def consolecmd():
# This function handles the console and client command.  Probably need to modify for use with XA
    argc = es.getargc()
    playerid = es.getcmduserid()
    if argc == 1:
        es.keygroupcreate("xaskins")
        j = 0
        for i in skinmenu:
            es.keycreate("xaskins", i)
            es.keysetvalue("xaskins", i, "skinmenu", skinnames[j])
            j+=1
        a = keymenu.create("xaskinmenu", "_keymenu_select", "xaskins/selectmenu", "xaskins", "#key", "#keyvalue skinmenu", "Skinlist\nSelect a Skin Menu")
        a.send(playerid)
        es.keygroupdelete("xaskins")

def selectmenu():
# This function makes the submenu for whichever set of skins was chosen
    es.keycreate('xaskinuser' + server_var['_popup_userid'])
    es.keysetvalue('xaskinuser' + server_var['_popup_userid'], 'skinset', server_var['_keymenu_select'])
    a = keymenu.create("xaskinmenu", "_keymenu_select", "xaskins/selectsubmenu", server_var['_keymenu_select'] + "skin", "#key", "#key", "Skinlist\nSelect a Skin Menu")
    a.send(server_var['_popup_userid'])

def selectsubmenu():
# In this function we need to set the model path into the player's settings
    mykey = es.keygetvalue('xaskinuser' + server_var['_popup_userid'], 'skinset') + 'skin'
    myskin = es.keygetvalue(mykey, server_var['_keymenu_select'], 'skin')
    es.keydelete('xaskinuser' + server_var['_popup_userid'])
# This line is just here to print your choice to the console.
    print mykey, server_var['_keymenu_select'], myskin
    
def add_skin_files(skin, i):
# This function reads in the 7 main skin files and parses each one
    fp = open(server_var['eventscripts_gamedir'] + "/cfg/mani_admin_plugin/skins/" + skin[i] +".txt")
    es.keygroupcreate(skin[i] + "skin")
    for line in fp:
        line = line.strip("\n")
        line = line.strip("\r")
        if line[0:1] == '"':
            skinfile = line[findsplit(line)+1:len(line)]
            skinname = line[0:findsplit(line)]
            skinname = skinname.strip('"')
#            modelname = ''
            skinmodel = makedownloadable(skinfile,skin[i])
            es.keycreate(skin[i] + "skin", skinname)
            es.keysetvalue(skin[i] + "skin", skinname, 'skin', skinmodel)
            
def makedownloadable(skinfile,skingroup):
# This function reads each model/material list files and makes them downloadable if cvar set.  Also returns model name
    sp =open(server_var['eventscripts_gamedir'] + "/cfg/mani_admin_plugin/skins/" + skingroup + "/" + skinfile)
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
