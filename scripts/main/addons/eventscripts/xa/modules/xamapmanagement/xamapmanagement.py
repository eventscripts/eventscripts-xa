import es
import popuplib
import xa.language
from xa import xa
import os.path
import string

gActions = {}
gMapCycle = []
gCurrentMap = None
gDefaultMaps = ('cs_assault','cs_compound','cs_havana','cs_italy','cs_militia','cs_office','de_aztec','de_cbble','de_chateau','de_dust','de_dust2','de_inferno','de_nuke','de_piranesi','de_port','de_prodigy','de_tides','de_train')

xamapmanagement = xa.register('xamapmanagement')
xalanguage = xa.language.getLanguage(xamapmanagement)

nextmapvar = es.ServerVar('eventscripts_nextmapoverride')
gamedir = str(es.ServerVar('eventscripts_gamedir'))

def load():
    xamapmainmenu = popuplib.easymenu('xamapmainmenu',None,xamapmainmenu_handler)
    xamapmainmenu.settitle(xalanguage['map management'])
    xamapmainmenu.addoption('changemap',xalanguage['change map'])
    xamapmainmenu.addoption('setnextmap',xalanguage['set map'])
    xamapmanagement.addMenu('xamapmainmenu',xalanguage['map management'],'xamapmainmenu','manage_maps','#admin')
    xamapmanagement.addCommand('nextmap',show_nextmap,'nextmap','#all').register(('console', 'say'))
    xamapmanagement.addCommand('xa_setnextmap',set_nextmap,'manage_maps','#admin').register(('server','console'))
    map_menu()
    map_cycle()

def unload():
    xa.unregister("xamapmanagement")

def es_map_start(event_var):
    global gCurrentMap
    map_menu()
    map_cycle()
    if event_var['mapname'] in gMapCycle:
        if not gCurrentMap or (gMapCycle.index(event_var['mapname']) != gCurrentMap+1):
            gCurrentMap = gMapCycle.index(event_var['mapname'])
        else:
            gCurrentMap += 1
    else:
        gCurrentMap = -1

def map_check(mapname):
    if mapname in gDefaultMaps or os.path.isfile(gamedir + '/maps/%s.bsp' % mapname):
        return True
    else:
        if not mapname.startswith('//'):
            es.dbgmsg(0, 'XAMapManagement: Unable to find map: %s.' % mapname)
        return False

def map_menu():
    if popuplib.exists('xamapmenu'):
        popuplib.delete('xamapmenu')
    maplist_path = gamedir + '/maplist.txt'
    if os.path.isfile(maplist_path):
        mapfile = open(maplist_path, 'r')
        maplist = filter(map_check,map(string.strip,mapfile.readlines()))
        mapfile.close()
        if 'test_speakers' in maplist:
            maplist.remove('test_speakers')
        if 'test_hardware' in maplist:
            maplist.remove('test_hardware')
        maplist.sort()
    else:
        maplist = gDefaultMaps
    xamapmenu = popuplib.easymenu('xamapmenu',None,mapmenu_handler)
    xamapmenu.settitle('Choose a map:')
    for mapname in maplist:
        xamapmenu.addoption(mapname,mapname)

def map_cycle():
    global gMapCycle
    gMapCycle = []
    mapcycle_path = gamedir + '/' + str(es.ServerVar('mapcyclefile'))
    if os.path.isfile(mapcycle_path):
        mapfile = open(mapcycle_path, 'r')
        gMapCycle = filter(map_check,map(string.strip,mapfile.readlines()))
        mapfile.close()
    else:
        gMapCycle = [es.ServerVar('eventscripts_currentmap')]

def show_nextmap():
    userid = es.getcmduserid()
    if str(nextmapvar) != '':
        nextmap = str(nextmapvar)
    else:
        nextmap = gMapCycle[gCurrentMap+1]
    es.tell(userid,'Next map: '+nextmap)

def xamapmainmenu_handler(userid,choice,popupname):
    gActions[userid] = choice
    popuplib.send('xamapmenu',userid)

def mapmenu_handler(userid,choice,popupname):
    if gActions[userid] == 'changemap':
        es.server.cmd('changelevel '+choice)
    elif gActions[userid] == 'setnextmap':
        nextmapvar.set(choice)
    del gActions[userid]

def set_nextmap():
    mapname = es.getargv(1)
    if map_check(mapname):
        nextmapvar.set(mapname)
    else:
        userid = int(es.getcmduserid())
        if userid:
            es.tell(userid,'#multi','#green[XA] #default',xalanguage['map management',{'mapname':mapname}])

            


