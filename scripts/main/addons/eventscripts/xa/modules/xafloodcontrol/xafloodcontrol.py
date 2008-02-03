import es
import os
import time
import xa
import xa.setting
from xa import xa

global timer
timer = {}

#plugin information
info = es.AddonInfo()
info.name = "Flood Control"
info.version = "0.1"
info.author = "Venjax"
info.url = "http://forums.mattie.info"
info.description = "Clone of Mani Flood Control feature for XA"
info.tags = "admin flood control XA"

xafloodcontrol = xa.register('xafloodcontrol')
chat_flood_time = xa.setting.createVariable('xafloodcontrol', 'chat_flood_time', '1.5')
chat_flood_message = xa.setting.createVariable('xafloodcontrol', 'chat_flood_message', 'Stop Spaming the server!')

def floodcontrol(userid, message, teamonly):
    #floodcontrol function. Eats spam according to time set in config options.
    global timer
    try:
        if not userid in timer.keys():
         timer[userid] = time.time()
         return userid, message, teamonly
        else:
         if time.time() - float(chat_flood_time) < timer[userid]:
             es.tell(userid, chat_flood_message)
             timer[userid] = time.time()
             return 0, message, teamonly
         else:
             timer[userid] = time.time()
             return userid, message, teamonly
    except Exception, inst:
         es.dbgmsg(0, "Error: ", inst)
         return userid, message, teamonly
           
def load():
    #Load Function for Chat Flood Control for XA.
    if chat_flood_time != '0':
        if not floodcontrol in es.addons.SayListeners:
            es.addons.registerSayFilter(floodcontrol)
        else:
            es.dbgmsg(0, 'chat_flood_time set to 0, exiting...')

def server_cvar(event_var):
    if event_var['cvarname'] == xa.setting.getVariableName('chat_flood_time'):
        if event_var['cvarvalue'] == '0':
            if floodcontrol in es.addons.SayListeners:
                es.addons.unregisterSayFilter(floodcontrol)
        else:
            if not floodcontrol in es.addons.SayListeners:
                es.addons.registerSayFilter(floodcontrol)

def unload():
    #Unloads XA Flood Control, and unregisteres saylisteners - if registered
    xa.unRegister(xafloodcontrol)
    if floodcontrol in es.addons.SayListeners:
        es.addons.unregisterSayFilter(floodcontrol)

def es_map_load():
    timer.clear()
