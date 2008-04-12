# Import ES and other modules 
import es 
import votelib 
import popuplib 
import playerlib 
import gamethread 

# Import XA 
from xa import xa 

vote_admins = {} 
vote_counter = {} 
vote_players = {} 

####################################### 
# ADDON INFORMATION 
# This describes the XA module 
info = es.AddonInfo() 
info.name           = "Vote" 
info.version        = "0.1" 
info.author         = "freddukes" 
info.url            = "http://forums.mattie.info/" 
info.description    = "Vote Module for eXtensible Admin" 

####################################### 
# MODULE NAME 
mymodulename = "xavote" 
mymodule = xa.register(mymodulename) 

####################################### 
# SERVER VARIABLES 
vote_timer = mymodule.setting.createVariable('vote_timer', 30, "How long in seconds that a vote will last for.") 
vote_start_sound = mymodule.setting.createVariable("vote_start_sound","ambient/machines/teleport4.wav","The sound that will be played when a vote is started") 
vote_end_sound = mymodule.setting.createVariable("vote_end_sound","ambient/alarms/warningbell1.wav","The sound that will be played when a vote is ended") 

####################################### 
# GLOBALS 
# Initialize our general global data here. 
# Localization helper: 
xalanguage = mymodule.language.getLanguage() 

if xa.isManiMode(): 
    xavotelist = mymodule.configparser.getList('cfg/mani_admin_plugin/votequestionlist.txt', True) 
else: 
    xavotelist = mymodule.configparser.getList('questionvotelist.txt') 
    
if xa.isManiMode(): 
    xavoterconlist = mymodule.configparser.getList('cfg/mani_admin_plugin/voterconlist.txt', True) 
else: 
    xavoterconlist = mymodule.configparser.getList('rconvotelist.txt') 

####################################### 
# LOAD AND UNLOAD 
# Formal system registration and unregistration 
def load(): 
    global _vote_active 
    xavotemenu = popuplib.easymenu("xavotemenu", "_vote_type", _vote_option) 
    xavotemenu.settitle(xalanguage["select vote"]) 
    xavotemenu.addoption("createvote",xalanguage["create vote"]) 
    xavotemenu.addoption("rconvote",xalanguage["rcon vote"]) 
    xavotemenu.addoption("questionvote",xalanguage["question vote"]) 
    xarconvote = popuplib.easymenu("xarconvote", "_rcon_vote", _rcon_vote) 
    xarconvote.settitle(xalanguage("rcon vote")) 
    xaquestionvote = popuplib.easymenu("xaquestionvote", "_question_vote", _question_vote) 
    xaquestionvote.settitle(xalanguage("question vote")) 
    
    if xavoterconlist:
        for line in xavoterconlist: 
            _get_rcon_votelist(xarconvote, line) 
    
    if xavotelist:
        for line in xavotelist: 
            _get_question_votelist(xaquestionvote, line) 
    
    mymodule.addMenu("xavotemenu", xalanguage["vote"], "xavotemenu", "start_vote", "#admin") 
    mymodule.addCommand("xa_set_title", _xa_set_title, "set_a_title", "#all").register("console") 
    mymodule.addCommand("xa_set_options", _xa_set_options, "set_vote_option", "#all").register("console") 
    mymodule.logging.log('xavote loaded') 
    _vote_active = 0 
    
def unload(): 
    popuplib.delete("xavotemenu") 
    mymodule.logging.log('xavote unloaded') 
    xa.unregister(mymodule) 
    
####################################### 
# Events 
# 
def player_connect(event_var): 
    vote_players[event_var['userid']] = {'stopped':0,'reason':None} 

def player_disconnect(event_var): 
    del vote_players[event_var['userid']] 
    if vote_admins.has_key(event_var['userid']): 
        del vote_admins[event_var['userid']] 
    
####################################### 
# MODULE FUNCTIONS 
# Register your functions here 
def _get_question_votelist(popup, line): 
    if not line.startswith('//') or line != '' : 
        line = line.split('"') 
        title = line[1] 
        question = line[3] 
        popup.addoption(question,title) 

def _get_rcon_votelist(popup, line): 
    if not line.startswith('//') or line != '': 
        line = line.split('"') 
        title = line[1] 
        question = line[3] 
        command = line[4] 
        command = command.split('//') 
        command = command[0] 
        popup.addoption(question + '^^^' + command,title) 

def _vote_option(adminid, vote_type, name): 
    if vote_type == "createvote": 
        _create_vote_title(adminid) 
    elif vote_type == "rconvote": 
        popuplib.send("xarconvote",adminid) 
    elif vote_type == "questionvote": 
        popuplib.send("xaquestionvote",adminid) 
        
def _create_vote_title(adminid): 
    if not _vote_active: 
        _select_vote_title = xalanguage("select vote title") 
        es.escinputbox(30, adminid, _select_vote_title, _select_vote_title, 'xa_set_title') 
        es.tell(adminid,'#green',xalanguage("escape prompt")) 
    else: 
        es.tell(adminid,'#green',xalanguage("already active")) 
    
def _xa_set_title(): 
    adminid = es.getcmduserid() 
    _vote_title = '' 
    _vote_index = 1 
    while _vote_index <= es.getargc(): 
        _vote_title = _vote_title + ' ' + str(es.getargv(_vote_index)) 
        _vote_index += 1 
    if vote_admins.has_key(str(adminid)): 
        vote_admins[str(adminid)]['title'] = _vote_title 
    else: 
        vote_admins[str(adminid)] = {'title':_vote_title} 
    es.escinputbox(30, adminid, xalanguage("vote options"), xalanguage("select vote options"), 'xa_set_options') 
    
def _xa_set_options(): 
    global _vote_active 
    adminid = es.getcmduserid() 
    _vote_title = vote_admins[str(adminid)]['title'] 
    _vote_options = '' 
    _vote_index = 1 
    while _vote_index <= es.getargc(): 
        _vote_options = _vote_options + ' ' + str(es.getargv(_vote_index)) 
        _vote_index += 1 
    vote_admins[str(adminid)]['options'] = _vote_options 
    _vote_options = _vote_options.split(",") 
    mymodule.logging.log('Admin ' + es.getplayername(adminid) + ' has started a vote:') 
    mymodule.logging.log('Title: ' + _vote_title) 
    index = 0 
    for a in _vote_options: 
        index += 1 
        mymodule.logging.log('Vote option ' + str(index) + ': ' + a) 
    # The vote title now equals _vote_title 
    # The vote options now equla _vote_options 
    _vote_menu = votelib.create(str(adminid),_vote_win,_vote_message) 
    _vote_menu.showmenu = False 
    _vote_menu.setquestion(_vote_title) 
    vote_counter.clear() 
    for a in _vote_options: 
        _vote_menu.addoption(a) 
        vote_counter[a] = 0 
    _vote_menu.start(vote_timer) 
    for a in vote_players: 
        if not vote_players[a]['stopped']: 
            popuplib.send("_vote_"+str(adminid),a) 
        elif vote_players[a]['reason']: 
            tokens = {} 
            tokens['reason'] = vote_players[a]['reason'] 
            es.tell(a,'#green',xalanguage("stopped vote",tokens)) 
    es.cexec_all('playgamesound',vote_start_sound) 
    gamethread.delayedname(1,'update_hint',UpdateHudHint, vote_counter) 
    _vote_active = 1 

def UpdateHudHint(vote_counter): 
    _sorted_vote_list = sorted(vote_counter, _sort_votes) 
    es.usermsg("create", "hudhint", "HintText") 
    es.usermsg("write","short","hudhint",-1) 
    format = "Vote Counter:\n-----------------------\n" 
    for index in range(min(2, len(_sorted_vote_list))): 
        _option = _sorted_vote_list[index] 
        format = format + _option + " - Votes: " + str(vote_counter[_option]) + "\n" 
    es.usermsg("write","string","hudhint",format) 
    for player in es.getUseridList(): 
        es.usermsg("send","hudhint",player,0) 
    es.usermsg("delete","hudhint") 
    gamethread.delayedname(5,'update_hint',UpdateHudHint,vote_counter) 

def _sort_votes(vote_1, vote_2): 
    if vote_counter[vote_1] >  vote_counter[vote_2]: return -1 
    if vote_counter[vote_1] == vote_counter[vote_2]: return 0 
    return 1 
    
def _vote_message(userid, votename, optionid, option): 
    tokens = {} 
    tokens['username'] = es.getplayername(userid) 
    tokens['option'] = str(option) 
    for player in es.getUseridList(): 
        es.tell(player,'#multi',xalanguage("vote message",tokens)) 
    if vote_counter.has_key(option): 
        vote_counter[option] += 1 
    else: 
        vote_counter[option] = 0 
    gamethread.cancelDelayed('update_hint') 
    UpdateHudHint(vote_counter) 
    
def _vote_win(popupid, optionid, choice, winner_votes, winner_percent, total_votes, was_tied, was_canceled): 
    global _vote_active 
    gamethread.cancelDelayed('update_hint') 
    _vote_active = 0 
    es.cexec_all('playgamesound',vote_end_sound) 
    tokens = {} 
    if not was_tied or was_canceled: 
        tokens['winner'] = choice 
        tokens['votes'] = winner_votes 
        tokens['totalvotes'] = total_votes 
        tokens['percent'] = winner_percent 
        for player in es.getUseridList(): 
            es.tell(player,'#multi',xalanguage("vote win",tokens)) 
    elif was_tied and not was_canceled: 
        for player in es.getUseridList(): 
            es.tell(player,'#green',xalanguage("vote tie")) 
        _sorted_vote_list = sorted(vote_counter, _sort_votes) 
        _vote_option_1 = _sorted_vote_list[0] 
        _vote_option_2 = _sorted_vote_list[1] 
        _vote_choice = random.choice[_vote_option_1,_vote_option_2] 
        tokens = {} 
        tokens['winner'] = choice 
        for player in es.getUseridList(): 
            es.tell(player,'#multi',xalanguage("random win", tokens)) 
    else: 
        for player in es.getUseridList(): 
            es.tell(player,'#green',xalanguage("vote canceled")) 
            
def _rcon_vote(adminid, _vote, name): 
    global _vote_active 
    global _rcon_command 
    if not _vote_active: 
        _vote_active = 1 
        vote_counter.clear() 
        _vote = _vote.split('^^^') 
        _vote_question = _vote[0] 
        _rcon_command = _vote[1] 
        _vote_menu = votelib.create(str(adminid),_rcon_win,_vote_message) 
        _vote_menu.showmenu = False 
        _vote_menu.setquestion(_vote_question) 
        _vote_menu.addoption(xalanguage("yes")) 
        _vote_menu.addoption(xalanguage("no")) 
        vote_counter["Yes"] = 0 
        vote_counter["No"] = 0 
        _vote_menu.start(vote_timer) 
        for a in vote_players: 
            if not vote_players[a]['stopped']: 
                popuplib.send("_vote_"+str(adminid),a) 
            elif vote_players[a]['reason']: 
                tokens = {} 
                tokens['reason'] = vote_players[a]['reason'] 
                es.tell(a,'#green',xalanguage("stopped vote",tokens)) 
        es.cexec_all('playgamesound',vote_start_sound) 
        gamethread.delayedname(1,'update_hint',UpdateHudHint, vote_counter) 
    else: 
        es.tell(adminid,'#green',xalanguage("already active")) 
            
def _rcon_win(popupid, optionid, choice, winner_votes, winner_percent, total_votes, was_tied, was_canceled): 
    global _vote_active 
    global _rcon_command 
    _vote_active = 0 
    es.cexec_all('playgamesound',vote_end_sound) 
    gamethread.cancelDelayed('update_hint') 
    if not was_tied or was_canceled: 
        if choice == "Yes": 
            es.server.cmd(_rcon_command) 
        _rcon_command = None 
        tokens = {} 
        tokens['winner'] = choice 
        tokens['votes'] = winner_votes 
        tokens['totalvotes'] = total_votes 
        tokens['percent'] = winner_percent 
        for player in es.getUseridList(): 
            es.tell(player,'#multi',xalanguage("vote win",tokens)) 
    elif was_tied and not was_canceled: 
        for player in es.getUseridList(): 
            es.tell(player,'#green',xalanguage("vote tie")) 
        winner = random.choice["yes","no"] 
        tokens = {} 
        tokens['winner'] = xalanguage(winner) 
        for player in es.getUseridList(): 
            es.tell(player,'#multi',xalanguage("random win", tokens)) 
    else: 
        for player in es.getUseridList(): 
            es.tell(player,'#green',xalanguage("vote canceled")) 
            
def _question_vote(adminid, _vote, name): 
    global _vote_active 
    if not _vote_active: 
        _vote_active = 1 
        vote_counter.clear() 
        _vote_menu = votelib.create(str(adminid),_vote_win,_vote_message) 
        _vote_menu.showmenu = False 
        _vote_menu.setquestion(_vote) 
        _vote_menu.addoption(xalanguage("yes")) 
        _vote_menu.addoption(xalanguage("no")) 
        vote_counter["Yes"] = 0 
        vote_counter["No"] = 0 
        _vote_menu.start(vote_timer) 
        for a in vote_players: 
            if not vote_players[a]['stopped']: 
                popuplib.send("_vote_"+str(adminid),a) 
            elif vote_players[a]['reason']: 
                tokens = {} 
                tokens['reason'] = vote_players[a]['reason'] 
                es.tell(a,'#green',xalanguage("stopped vote",tokens)) 
        es.cexec_all('playgamesound',vote_start_sound) 
        gamethread.delayedname(1,'update_hint',UpdateHudHint, vote_counter) 
    else: 
        es.tell(adminid,'#green',xalanguage("already active")) 

def stopVoting(userid,reason=''): 
    vote_players[userid]['stopped'] = 1 
    if reason: 
        vote_players[userid]['reason'] = reason
