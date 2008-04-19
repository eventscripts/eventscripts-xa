import es 
import gamethread 
import playerlib
import time
from xa import xa 

#plugin information 
info = es.AddonInfo() 
info.name     = 'XA Spawn & Team Kill/Attack Protection' 
info.version  = '1.0.0' 
info.url      = 'http://forums.mattie.info/cs/forums/viewtopic.php?t=19690' 
info.basename = 'xaprotect' 
info.author   = 'Errant' 

''' 
Provides basic spawn protection and damage reflection

== V1.0.0 ==
 - Released publicly
 - Name change to XAProtect
 - [+] Team kill protection
 - [FIX] Changed the protection levels from 5000 to 1124
== OY1 ==
 - [+] Added basic spawn protection (raised health)
 - [+] Added the ability to kill people who spawn kill
 - [+] Added reflect damage ability against team wounders
''' 

class twPlayer(object): 
    def __init__(self, userid): 
        # set up a player instance of playlib 
        self.uid = int(userid) 
        # some more stuff of use 
        self.plib = playerlib.getPlayer(self.uid) 
        self.steamid = es.getplayersteamid(self.uid) 
        # get some initial data 
        self.spawntime = False 
    


class twPHandler(object): 
    def __init__(self): 
        self.players = {} 
    def addPlayer(self, userid): 
        uid = int(userid) 
        self.players[uid] = twPlayer(uid) 
    def removePlayer(self, userid): 
        uid = int(userid) 
        if uid in self.players: 
            self.players.pop(uid, 0) 
    def protect(self, userid): 
        p = self.grab(userid) 
        if p: 
            p.set("health", 1124) 
    def unprotect(self, userid): 
        p = self.grab(userid) 
        if p: 
            p.set("health", 100) 
    def set(self, userid, setting, value): 
        p = self.grab(userid) 
        if p: 
            p.set(setting, value) 
    def getspawntime(self, userid): 
        uid = int(userid) 
        if uid in self.players: 
            return self.players[uid].spawntime 
        return False 
    def setspawntime(self, userid, value): 
        uid = int(userid) 
        if uid in self.players: 
            self.players[uid].spawntime = value 
    def get(self, userid, setting): 
        p = self.grab(userid) 
        if p: 
            return p.get(setting) 
        return False 
    def grab(self, userid): 
        uid = int(userid) 
        if uid in self.players: 
            return self.players[uid].plib 
        return False 
    def reflect(self, a, v, damage): 
        attacker = self.grab(a) 
        victim = self.grab(v) 
        if attacker.get("team") == victim.get("team"): 
            multiplier = int(module.setting.getVariable('protect_reflect_damage_percentage')) 
            if multiplier > 10: 
                multiplier = 10 
            elif multiplier < 0: 
                multiplier = 0 
            attacker.set("health", (((int(attacker.get("health")) - int(damage)) / 10) * multiplier)) 
    def team_killattack(self, a, v):  
        attacker = self.grab(a) 
        victim = self.grab(v) 
        if attacker.get("team") == victim.get("team"):
            attacker.kill()
            
# register module with XA 
module = xa.register('xaprotect') 

# Localization helper: 
#text = module.language.getLanguage('xaprotect') 

# make config vars 
module.setting.createVariable('protect_wound', 1, '1 = ON, 0 = OFF') 
module.setting.createVariable('protect_spawn_protection_time', 3, 'The number of seconds to make people invulnerable at spawn (0 = OFF)') 
module.setting.createVariable('protect_spawn_protection_mode', 0, '(1 = Anytime players spawn, 0 = Only at round start)') 
module.setting.createVariable('protect_reflect_damage', 0, '(0 = OFF, 1 = Reflect all damage, 2 = reflect some damage)') 
module.setting.createVariable('protect_reflect_damage_percentage', 10, '(0 to 10: the percentage of damage to reflect)') 
module.setting.createVariable('protect_spawn_slay', 0, 'Slay spawn attackers(0=OFF, 1=ON)') 
module.setting.createVariable('protect_spawn_slay_time', 3, '# of seconds after spawning an attacker is slayed for team attacking')    
module.setting.createVariable('protect_teamkill_slay', 0, 'Slay team killers(0=OFF, 1=ON)') 
module.setting.createVariable('protect_teamattack_slay', 0, 'Slay team attackers(0=OFF, 1=ON)') 

# init player handler      
plist = twPHandler()  
  
def unload(): 
    xa.unregister('xateamwound')
    
def player_team(event_var): 
    if int(event_var["userid"]) not in plist.players: 
        plist.addPlayer(event_var["userid"]) 
    
    
def player_spawn(event_var): 
    ''' 
     = OY1 = 
     [+] Spawn protection (raises health for set # of seconds) 
    ''' 
    prtime = int(module.setting.getVariable('protect_spawn_protection_time'))
    prmode = int(module.setting.getVariable('protect_spawn_protection_mode'))
    if prtime > 0: 
        # initiate spawn protection 
        if prmode == 0 and roundstatus == 0: 
            # protect the player 
            plist.protect(event_var['userid']) 
            # after the set delay remove the "protection" 
            gamethread.delayed(prtime, plist.unprotect, (event_var['userid'])) 
        elif prmode == 0: 
            # protect the player 
            plist.protect(event_var['userid']) 
            # after the set delay remove the "protection" 
            gamethread.delayed(prtime, plist.unprotect, (event_var['userid'])) 

def player_hurt(event_var): 
    ''' 
    == OY1 == 
     [+] Added reflect damage 
     [+] Spawn slay protection 
    ''' 
    if int(module.setting.getVariable('protect_reflect_damage')): 
        # were reflecting damage 
        plist.reflect(event_var["es_attackerid"], event_var["userid"], event_var["damage"]) 
    if int(module.setting.getVariable('protect_spawn_slay')): 
        timelimit = plist.getspawntime(event_var["userid"]) + int(module.setting.getVariable('protect_spawn_slay_time')) 
        if time.time() < timelimit: 
            # oops! kill them 
            plist.grab(event_var["attackerid"]).kill() 
    if int(module.setting.getVariable('protect_teamattack_slay')): 
        plist.team_killattack(event_var["es_attackerid"], event_var["userid"])
       
def player_death(event_var):
    '''
    == 1.0.0 ==
     [+] Team kill protect
    '''
    if int(module.setting.getVariable('protect_teamkill_slay')) and not int(module.setting.getVariable('protect_teamattack_slay')): 
        plist.team_killattack(event_var["es_attackerid"], event_var["userid"])
    
def round_start(event_var):  
    global roundstatus, round_start_time 
    roundstatus = 1 
    round_start_time = time.time() 

def round_end(event_var):  
    global roundstatus, round_start_time 
    roundstatus = 0 
  
def player_spawn(event_var):  
    plist.setspawntime(event_var["userid"], time.time()) 
    
def player_disconnect(event_var): 
    plist.removePlayer(event_var["userid"]) 

def load(): 
    xa.register('xateamwound')
