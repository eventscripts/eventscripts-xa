import es 
import playerlib 
import usermsg 
import xa 
import xa.logging 
import xa.setting 
from xa import xa 

def load(): 
    """ """ 
    global mymodule 
    ####################################### 
    # MODULE NAME 
    # This is the name of the module. 
    mymodulename = "xarates" 
    # Register the module 
    # this is a global reference to your module 
    mymodule = xa.register(mymodulename) 
    xa.logging.log(mymodule, 'xarates loaded') 
    mymodule.addCommand('xa_rates', xarates_cmd, 'display_rates', '#all').register(('console')) 

def unload(): 
    xa.logging.log(mymodule, 'xarates unloaded') 
    xa.unRegister('xarates') 

def xarates_cmd(): 
    int_userid = es.getcmduserid() 
    xa.logging.log(mymodule, 'xarates request by %s (%s)' % (es.getplayersteamid(int_userid), es.getplayername(int_userid))) 
    dict_rates = {} 
    longest_name = 4 
    longest_rate = 4 
    longest_cmdrate = 8 
    longest_updaterate = 11 
    longest_interp = 6 
    for instance_player in playerlib.getPlayerList("#all"): 
        int_player = int(instance_player) 
        if es.getplayersteamid(int_player) != "BOT": 
            str_name = es.getplayername(int_player) 
            if len(str_name) > longest_name: 
                longest_name = len(str_name) 
            dict_rates[int_player] = {} 
            str_rate = es.getclientvar(int_player, "rate") 
            dict_rates[int_player]["rate"] = str_rate 
            if len(str_rate) > longest_rate: 
                longest_rate = len(str_rate) 
            str_cmdrate = es.getclientvar(int_player, "cl_cmdrate") 
            dict_rates[int_player]["cmdrate"] = str_cmdrate 
            if len(str_cmdrate) > longest_cmdrate: 
                longest_cmdrate = len(str_cmdrate) 
            str_updaterate = es.getclientvar(int_player, "cl_updaterate") 
            dict_rates[int_player]["updaterate"] = str_updaterate 
            if len(str_updaterate) > longest_updaterate: 
                longest_updaterate = len(str_updaterate) 
            str_interp = es.getclientvar(int_player, "cl_interp") 
            dict_rates[int_player]["interp"] = str_interp 
            if len(str_interp) > longest_interp: 
                longest_interp = len(str_interp) 
    total_len = longest_name + longest_rate + longest_cmdrate + longest_updaterate + longest_interp + 12 
    usermsg.echo(int_userid, "|%s|" % ("-" * total_len)) 
    usermsg.echo(int_userid, "|%-*s   %-*s   %-*s   %-*s   %-*s|" % (longest_name, "Name", longest_rate, "Rate", longest_cmdrate, "CMD Rate", longest_updaterate, "Update Rate", longest_interp, "Interp")) 
    usermsg.echo(int_userid, "|%s|" % ("-" * total_len)) 
    for int_player in dict_rates: 
        usermsg.echo(int_userid, "|%-*s   %-*s   %-*s   %-*s   %-*s|" % (longest_name, es.getplayername(int_player), longest_rate, dict_rates[int_player]["rate"], longest_cmdrate, dict_rates[int_player]["cmdrate"], longest_updaterate, dict_rates[int_player]["updaterate"], longest_interp, dict_rates[int_player]["interp"])) 
    usermsg.echo(int_userid, "|%s|" % ("-" * total_len))