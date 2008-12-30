import es
import gamethread
import playerlib
import popuplib
import votelib
import random
import time
from xa import xa 

info = es.AddonInfo() 
info.name       = "Rock the Vote" 
info.version    = "0.01" 
info.author     = "[#OMEGA] - K2" 
info.url        = "http://forums.mattie.info" 
info.description    = "Rock the Vote Module for XA" 
info.tags       = "rock the vote rtv rockthevote" 

''' 
Credits: 

me (obviously)  

Changelog: 

Version 0.01: 

-release 

ToDo: 

-Add option in admin menu to cancel RTV 
-Option & command for refreshing variables 
-Admin & Server command to cancel RTV 
-Output to server console (logging excluded) 
-mapchange protection 
-find a better way to open the mapfiles 
-german translation of strings.ini (0.02) 

Notes: 

''' 

xartv = xa.register('xarockthevote') 

vote_req_setmap_p   = xartv.setting.createVariable('vote_rock_the_vote_percent_required', 60, "Defines the vote percentage required to set map (0 min, 100max)") 
vote_req_time       = xartv.setting.createVariable('vote_time_before_rock_the_vote', 1, "Time before rockthevote can be started after a new map starts in seconds") #120 
vote_nominations    = xartv.setting.createVariable('vote_rock_the_vote_number_of_nominations', 6, "Number of nominations included in the vote (min 1,can't be higher than vote_rock_the_vote_number_of_maps)") 
vote_maps           = xartv.setting.createVariable('vote_rock_the_vote_number_of_maps', 6, "Number of random maps chosen from the maplistfile votemaplist.txt") 
vote_maplistfile    = xartv.setting.createVariable('vote_rock_the_vote_maplistfile', 'votemaplist.txt', "Defines the maplistfile (custom files must be located in /cstrike/)") 
vote_req_p          = xartv.setting.createVariable('vote_vote_rock_the_vote_threshold_percent', 60, "Percentage of players on server required to type rockthevote before it starts (min 1, max 100)") 
vote_req_min        = xartv.setting.createVariable('vote_rock_the_vote_threshold_minimum', 1, "Minimum number of players required to type rockthevote before it starts") #4 
vote_mapchange_time = xartv.setting.createVariable('vote_rock_the_vote_time_to_mapchange', 10, "The amount of time after which the map is changed to (1 min, 60max)") 

if not 1 <= vote_mapchange_time <= 60: 
    vote_mapchange_time = 10 
if not 1 <= vote_req_setmap_p <= 100: 
    vote_req_setmap_p  = 60 
if not 1 <= vote_req_p <= 100: 
    vote_req_p = 60 
if not 1 <= vote_nominations: 
    vote_nominations = 6 
if vote_nominations > vote_maps: 
    vote_nominations = vote_maps 

lang = xartv.language.getLanguage() 

# Globals 
votes_in = 0 
vote_req_total = 0 
map_start_time = time.time() 

players = {} 
# Structure of the dict: 
# {'playersteamid': [voted?,nominated?]} 

nominations = {}

def load(): 
    xartv.addCommand('rtv',rtv,'use_rtv','UNRESTRICTED').register(('say', 'console')) 
    xartv.addCommand('rockthevote',rtv,'use_rtv','UNRESTRICTED').register(('say', 'console')) 
    xartv.addCommand('nominate',nominate,'use_rtv','UNRESTRICTED').register(('say', 'console')) 
    global nomination_popup 
    nomination_popup = popuplib.easymenu('nomination_menu',None, nomination_result) 
    nomination_popup.settitle(lang['choose_map']) 
    maps = read_mapfile() 
    for map in maps: 
        nomination_popup.addoption(map,xartv.language.createLanguageString(map)) 

def unload(): 
    gamethread.cancelDelayed('rtv_mapchange')
    if votelib.isrunning('rockthevote'): 
        votelib.stop('rockthevote') 
    if votelib.exists('rockthevote'): 
        votelib.delete('rockthevote') 
    # Unregister the module 
    xartv.unregister() 

def entry(steamid): 
    if not players.has_key(steamid): 
        players[steamid] = [False,False] 
    
# Nomination System 
    
def nominate(): 
    userid = es.getcmduserid() 
    if not votelib.isrunning('rockthevote') and votes_in: 
        steamid = es.getplayersteamid(userid) 
        entry(steamid) 
        if not players[steamid][1]: 
            nomination_popup.send(userid) 
        else: 
            es.tell(userid,'#multi',lang('1nominate',lang=playerlib.getPlayer(userid).get('lang'))) 
    else: 
        es.tell(userid,'#multi',lang('no_nominate',lang=playerlib.getPlayer(userid).get('lang'))) 

def nomination_result(userid, choice, popupname):
    steamid = es.getplayersteamid(userid)
    players[steamid][1] = True 
    if not nominations.has_key(choice): 
        nominations[choice] = 1
    else: 
        # I might add support for "most" nominations later 
        nominations[choice] += 1
    name = es.getplayername(userid) 
    for userid in es.getUseridList(): 
        es.tell(userid,'#multi',lang('nominated',{'player': name,'mapname': choice},playerlib.getPlayer(userid).get('lang'))) 
    
# Rock The Vote 
    
def rtv(): 
    userid = es.getcmduserid() 
    steamid = es.getplayersteamid(userid) 
    entry(steamid) 
    if not players[steamid][0]: 
        players[steamid][0] = True
        global votes_in,vote_req_total 
        if (time.time() - map_start_time) < vote_req_time: 
            es.tell(userid,'#multi',lang('map_time',{'time': (120 - int((time.time() - map_start_time)))},playerlib.getPlayer(userid).get('lang'))) 
        else: 
            if not votelib.isrunning('rockthevote'): 
                if not votes_in: 
                    vote_req_total = int(vote_req_p * 0.01 * len(es.getUseridList())) 
                    name = es.getplayername(userid) 
                    for user in es.getUseridList(): 
                        es.tell(user,'#multi',lang('player_started',{'player': name},playerlib.getPlayer(user).get('lang'))) 
                        nomination_popup.unsend(user) 
                votes_in += 1 
                # Checks for percentage and for the amount of minium votes required 
                if votes_in >= vote_req_min: 
                    if votes_in >= vote_req_total: 
                        rtv_init() 
                    else: 
                        name = es.getplayername(userid) 
                        for user in es.getUseridList(): 
                            es.tell(user,'#multi',lang('req',{'player': name,'votes': (vote_req_total - votes_in)},playerlib.getPlayer(user).get('lang'))) 
                else: 
                    name = es.getplayername(userid) 
                    for user in es.getUseridList(): 
                        es.tell(user,'#multi',lang('req',{'player': name,'votes': (vote_req_min - votes_in)},playerlib.getPlayer(user).get('lang'))) 
            else: 
                es.tell(userid,'#multi',lang('started',lang=playerlib.getPlayer(userid).get('lang'))) 
    else: 
        es.tell(userid,'#multi',lang('1vote',lang=playerlib.getPlayer(userid).get('lang'))) 

def rtv_init(): 
    global vote_maps 
    maps = read_mapfile() 
    # Checks for the number of maps to be included 
    if vote_maps > len(maps): 
        vote_maps = len(maps) 
        xartv.logging.log("Number of maps to be included in rtv is too high - using all maps.") 
    # Get a list of the indexes of the random maps 
    rnd_maps = random_map(maps).get_results() 
    # Create the vote 
    rockthevote = votelib.create('rockthevote', rtv_finish, rtv_submit) 
    rockthevote.setquestion('Choose a map:') 
    # Add for everymap in the list a option 
    for index in rnd_maps: 
        rockthevote.addoption(maps[index]) 
    # Start the vote 
    rockthevote.start(45) 
    
class random_map: 
    found = 0 
    results = [] 
    length = 0 
    def __init__(self,maps): 
        self.results = [] 
        self.found = 0 
        self.length = len(maps) - 1 
        for map in nominations: 
            for i in range(0,self.length): 
                if maps[i] == map: 
                    self.found += 1 
                    self.results += [i] 
        self.loop() 
    def loop(self): 
        map_index = random.randint(0,self.length) 
        if map_index in self.results: 
            self.loop() 
        else: 
            self.results += [map_index] 
            self.found += 1 
            if not self.found == vote_maps: 
                self.loop() 
    def get_results(self): 
        return self.results 

def rtv_submit(userid, votename, choice, choicename): 
    for user in es.getUseridList(): 
        es.tell(user,'#multi',lang('voted',{'player': es.getplayername(userid),'mapname': choicename},playerlib.getPlayer(user).get('lang'))) 

def rtv_finish(votename, win, winname, winvotes, winpercent, total, tie, cancelled): 
    # Deletes vote so it can be re-created 
    votelib.delete('rockthevote') 
    if (float(total) / len(es.getUseridList())) >= (vote_req_setmap_p * 0.01): 
        for userid in es.getUseridList(): 
            es.tell(userid,'#multi',lang('success',{'mapname': winname,'time': vote_mapchange_time},playerlib.getPlayer(userid).get('lang'))) 
        gamethread.delayedname(vote_mapchange_time,'rtv_mapchange',rtv_map,winname) 
    else: 
        for userid in es.getUseridList(): 
            es.tell(userid,'#multi',lang('fail',lang=playerlib.getPlayer(userid).get('lang'))) 

def rtv_map(map): 
    xartv.logging.log('Changing map to %s...' % map) 
    # Removes all players from the dict 
    players.clear() 
    es.server.cmd('changelevel %s' % map) 
    
def read_mapfile(): 
    # Read the mapcycle file 
    if vote_maplistfile == "votemaplist.txt":
        if xa.isManiMode():
            maps = xartv.configparser.getList('cfg/mani_admin_plugin/%s' % vote_maplistfile, True)
        else:
            maps = xartv.configparser.getList(vote_maplistfile)
    else:
        maps = xartv.configparser.getList(vote_maplistfile, True)
    if not maps:
        maps = xartv.configparser.getList('maplist.txt', True)
    if not maps:
        maps = xartv.configparser.getList('mapcycle.txt', True)
    if not maps:
        maps = []
    return maps
# Events

def es_map_start(ev): 
    global map_start_time 
    map_start_time = time.time() 
    # Deletes and unsends vote 
    if votelib.isrunning('rockthevote'): 
        votelib.stop('rockthevote') 
    if votelib.exists('rockthevote'): 
        votelib.delete('rockthevote')
    for steamid in players:
        players[steamid] = [False,False]
