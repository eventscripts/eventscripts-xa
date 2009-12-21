import esimport playerlibimport popuplibfrom xa import xa#plugin informationinfo = es.AddonInfo()info.name           = "Player Management"info.version        = "0.2"info.author         = "Hunter"info.basename       = "xaplayers"manage_choice = {}manage_method = {}manage_display = {}manage_target = {}manage_targetlist = {}manage_pmenus = {}manage_argc = {}manage_cross_ref = {}ban_times = {}ban_times_order = []xaplayers                   = xa.register(info.basename)xalanguage                  = xaplayers.language.getLanguage()xa_adminkick_anonymous      = xaplayers.setting.createVariable('adminkick_anonymous', 0, "When an admin kicks a player, will no text be sent?")xa_adminban_anonymous       = xaplayers.setting.createVariable('adminban_anonymous', 0, "When an admin bans a player, will no text be sent?")xa_adminswap_anonymous      = xaplayers.setting.createVariable('adminswap_anonymous', 0, "When an admin swaps a player, will no text be sent?")xaplayers.setting.createCommandSpace("xa_ban_time", "xa_ban_time <add> <time limit in minutes> [Optional: permission]", """This will create an option to ban a player for that time length// This can also create a permission so you can allow some admins// to have the ability to ban for certain time lengths. If no permission is given// the permission ban_players is assumed. //      xa_ban_time add 0// The permission for that will be//      ban_player// The permission for "xa_ban_time add 0 ban_time_permanent" will be "ban_time_permanent"// which means only admins which have been given the "ban_time_permanent" permission// will be allowed to ban permenantly.// An example of a valid command is as follows://      xa_ban_time add 60 ban_time_hour// That command would add an option to ban a player for 1 hour.""")def load():    #Load Function for Player Settings for XA.    xaplayermenu = popuplib.easymenu("xaplayermenu", "_tempcore", _select_option)    xaplayermenu.settitle(xalanguage["choose option"])    xaplayers.addMenu("xaplayermenu", xalanguage["manage players"], "xaplayermenu", "manage_player", "ADMIN")        xaplayertargetmenu = popuplib.easymenu("xaplayertargetmenu", "_tempcore", _select_target)    xaplayertargetmenu.settitle(xalanguage["choose target"])    xaplayertargetmenu.addoption("player", xalanguage["select a player"])    xaplayertargetmenu.addoption("team3", xalanguage["counter terrorists"])    xaplayertargetmenu.addoption("team2", xalanguage["terrorists"])    xaplayertargetmenu.addoption("all", xalanguage["all players"])    xaplayertargetmenu.submenu(10, xaplayermenu)        xaplayersuremenu = popuplib.easymenu("xaplayersuremenu", "_tempcore", _select_sure)    xaplayersuremenu.settitle(xalanguage["are you sure"])    xaplayersuremenu.addoption(True, xalanguage["yes"])    xaplayersuremenu.addoption(False, xalanguage["no"])    xaplayersuremenu.submenu(10, xaplayertargetmenu)        xaplayers.registerOption("kick", xalanguage["kick"], _manage_kick, 1)    xaplayers.registerOption("ban",   xalanguage["ban"], _manage_ban, 1)    xaplayers.registerOption("swap", xalanguage["swap"], _manage_swap, 1)    xaplayers.registerOption("spec", xalanguage["spec"], _manage_spec, 1)        xaplayers.addCommand('xa_ban_time', addBanTime, "ban_time", "UNRESTRICTED", "ban_time <add> <amount of time in minutes>", True).register(('server',))         def unload():    for manage in manage_method:        xaplayers.unregisterOption(manage)    popuplib.delete("xaplayermenu")    popuplib.delete("xaplayertargetmenu")    popuplib.delete("xaplayersuremenu")    popuplib.delete("xabantimeselect")    for page in manage_pmenus:        manage_pmenus[page].delete()    xaplayers.unregister()    def _select_option(userid, choice, name):    manage_choice[userid] = choice    if not userid in manage_target:        popuplib.send("xaplayertargetmenu", userid)    else:        _manage_player(manage_target[userid], manage_choice[userid], userid)        del manage_target[userid]    def _select_target(userid, choice, name):    if choice == "player":        if userid in manage_pmenus:            manage_pmenus[userid].delete()        manage_pmenus[userid] = popuplib.construct("xamanageplayermenu"+str(userid), "players", "#all")        manage_pmenus[userid].settitle(xalanguage["choose player"])        manage_pmenus[userid].menuselectfb = _select_player        manage_pmenus[userid].submenu(10, "xaplayertargetmenu")        manage_pmenus[userid].send(userid)    else:        if choice == "team3":            playerlist = playerlib.getUseridList("#ct")        elif choice == "team2":            playerlist = playerlib.getUseridList("#t")        elif choice == "all":            playerlist = es.getUseridList()        if playerlist:            manage_targetlist[userid] = playerlist            popuplib.send("xaplayersuremenu", userid)        else:            popuplib.send("xaplayertargetmenu", userid)def _select_sure(userid, choice, name):    if choice and manage_targetlist[userid] and manage_choice[userid]:        for player in manage_targetlist[userid]:            _manage_player(player, manage_choice[userid], userid)    else:        popuplib.send("xaplayertargetmenu", userid)def _select_player(userid, choice, name):    _manage_player(choice, manage_choice[userid], userid)    def _command_player():    adminid = es.getcmduserid()    if adminid > 0:        admin = playerlib.getPlayer(adminid)    cmd = es.getargv(0).replace(str(es.ServerVar('xa_sayprefix')), 'xa_', 1).replace('ma_', 'xa_', 1)    if cmd in manage_cross_ref:        option = manage_cross_ref[cmd]        if option in manage_argc:            argc = es.getargc()            if argc > manage_argc[option]:                args = []                for i in range(1, argc):                    args.append(es.getargv(i))                user = es.getargv(1)                for userid in playerlib.getUseridList(user):                    _manage_player(userid, option, adminid, args)            elif adminid > 0:                es.tell(adminid, xalanguage("not enough args", (), admin.get("lang")))            else:                es.dbgmsg(0, xalanguage("not enough args"))def _manage_player(userid, option, adminid, args = [], force = False):    allowed = False    if option == "ban":        for time in ban_times_order:            tupleOfPermission = ban_times[time]            stringName, permission = tupleOfPermission            if xaplayers.isUseridAuthorized(adminid, permission):                allowed = True                break    if adminid == 0 or (xaplayers.isUseridAuthorized(adminid, option+"_player") or allowed) or force:        if (not xaplayers.isUseridAuthorized(userid, "immune_"+option)) or (userid == adminid) or force:            if callable(manage_method[option]):                xaplayers.logging.log("used option %s on user %s [%s]" % (option, es.getplayername(userid), es.getplayersteamid(userid) ), adminid, True )                try:                    manage_method[option](userid, adminid, args, force)                except TypeError:                    try:                        manage_method[option](userid, adminid, args)                    except TypeError:                        manage_method[option](userid, adminid)                return True            else:                es.dbgmsg(0, "xaplayers.py: Cannot find method '"+str(manage_method[option])+"'!")                return False        else:            es.tell(adminid, xalanguage("immune", {'username':es.getplayername(userid)}, playerlib.getPlayer(adminid).get("lang")))            return False    else:        es.tell(adminid, xalanguage("not allowed", (), playerlib.getPlayer(adminid).get("lang")))        return Falsedef registerOption(module, option, name, method, argc = 0):    if not option in manage_method:        manage_method[option] = method        manage_display[option] = name        manage_argc[option] = argc        manage_cross_ref['xa_'+option] = option        xaplayermenu = popuplib.find("xaplayermenu")        xaplayermenu.addoption(option, name, 1)        xaplayers.registerCapability("immune_"+option, "ADMIN", "IMMUNITY")        if manage_argc[option] > 0:            xaplayers.addCommand('xa_'+option, _command_player, option+"_player", "ADMIN", name["en"]+" option", True).register(('say', 'console','server'))        return True    else:        return False    def unregisterOption(module, option):    if option in manage_method:        xaplayermenu = popuplib.find("xaplayermenu")        xaplayermenu.addoption(option, 'Unloaded', 0)        if manage_argc[option] > 0:            xaplayers.delCommand('xa_'+option)        manage_method[option] = None        try:            del manage_display[option]            del manage_argc[option]            del manage_cross_ref['xa_'+option]        except:            pass        return True    else:        return False        def managePlayer(option, userid, adminid, args = [], force = False):    if option in manage_method:        return _manage_player(userid, option, adminid, args, force)    else:        return Falsedef sendPlayersMenu(userid, victimid):    for user in list(userid):        manage_target[user] = victimid        xaplayermenu.send(user)# The default options that ship with the moduledef _manage_kick(userid, adminid, args):    if str(xa_adminkick_anonymous) == '0':        tokens = {}        tokens['admin']   = es.getplayername(adminid)        tokens['user']    = es.getplayername(userid)        for user in playerlib.getPlayerList():            es.tell(user, xalanguage("admin kick", tokens, user.get("lang")))    es.server.queuecmd("kickid %s Kicked by Admin" % userid)def _manage_ban(userid, adminid, args=[]):    if len(args) > 1:        banPlayer(userid, adminid, args[1])    else:        tempPopup = popuplib.easymenu('xabantimelength_%s' % adminid, "_tempcore", _select_ban_time)        tempPopup.settitle("Select a time to ban a player")        for time in ban_times_order:            tupleOfInfo = ban_times[time]            if xaplayers.isUseridAuthorized(adminid, tupleOfInfo[1]):                tempPopup.addoption((time, userid), tupleOfInfo[0])        tempPopup.send(adminid)        def _select_ban_time(adminid, choice, popupid):    bantime, userid  = choice    banPlayer(userid, adminid, bantime)def banPlayer(userid, adminid, bantime):    if str(xa_adminban_anonymous) == '0':        tokens = {}        tokens['admin']   = es.getplayername(adminid)        tokens['user']    = es.getplayername(userid)        for user in playerlib.getPlayerList():            if int(bantime) > 0:                tokens['time']    = xalanguage("bantime", {'min': str(bantime)}, user.get("lang"))            else:                tokens['time']    = xalanguage("banperm", {}, user.get("lang"))            es.tell(user, xalanguage("admin ban", tokens, user.get("lang")))    xaplayers.logging.log("banned user %s [%s] for %s" % (es.getplayername(userid), es.getplayersteamid(userid), getTimeAsString(bantime) ), adminid, True )    es.server.queuecmd("banid %s %s" % (bantime, userid))    es.server.queuecmd("kickid %s Banned by Admin %s%s" % (userid, "for " if bantime > 0 else "", getTimeAsString(bantime) ) )def _manage_swap(userid, adminid, args):    if str(xa_adminswap_anonymous) == '0':        tokens = {}        tokens['admin']   = es.getplayername(adminid)        tokens['user']    = es.getplayername(userid)        for user in playerlib.getPlayerList():            es.tell(user, xalanguage("admin swap", tokens, user.get("lang")))    if int(es.getplayerteam(userid)) == 2:        es.server.queuecmd("es_xchangeteam %s 3" % userid)    elif int(es.getplayerteam(userid)) == 3:        es.server.queuecmd("es_xchangeteam %s 2" % userid)def _manage_spec(userid, adminid, args):    if str(xa_adminswap_anonymous) == '0':        tokens = {}        tokens['admin']   = es.getplayername(adminid)        tokens['user']    = es.getplayername(userid)        for user in playerlib.getPlayerList():            es.tell(user, xalanguage("admin spec", tokens, user.get("lang")))    if int(es.getplayerteam(userid)) != 1:        es.server.queuecmd("es_xchangeteam %s 1" % userid)def addBanTime():    args = [es.getargv(x) for x in xrange(1, es.getargc())]    if not len(args):        xaplayers.logging.log("Incorrect usage: xa_ban_time <add> <time in minutes> [permission] - you used: %s" % ('xa_ban_time'))        return    if args[0] != "add":        xaplayers.logging.log("Incorrect usage: xa_ban_time <add> <time in minutes> [permission] - you used: %s" % ('xa_ban_time %s' % ' '.join(args)))        return    if len(args) not in (2, 3):        xaplayers.logging.log("Incorrect usage: xa_ban_time <add> <time in minutes> [permission] - you used: %s" % ('xa_ban_time %s' % ' '.join(args)))        return    if not args[1].isdigit():        xaplayers.logging.log("Minutes is not an integer: xa_ban_time <add> <time in minutes> [permission] - you used: %s" % ('xa_ban_time %s' % ' '.join(args)))        return    args[1] = int(args[1])    if args[1] in ban_times:        xaplayers.logging.log("xa_ban_time add %s has already been used and recognised." % args[1])        return    ban_times[args[1]] = (getTimeAsString(args[1]), args[2] if len(args) == 3 else 'ban_player')    ban_times_order.append(args[1])     def getTimeAsString(minutes):    if minutes == 0:        return "Permanently"    if minutes < 0:        return "Unknown"    years,  minutes = divmod(minutes, 525600)    months, minutes = divmod(minutes, 43800)    weeks,  minutes = divmod(minutes, 10080)    days,   minutes = divmod(minutes, 1440)    hours,  minutes = divmod(minutes, 60)        currentTime = []    if years:        currentTime.append("%s year%s" % (years, 's' if years > 1 else ''))    if months:        currentTime.append("%s month%s" % (months, 's' if months > 1 else ''))    if weeks:        currentTime.append("%s week%s" % (weeks, 's' if weeks > 1 else ''))    if days:        currentTime.append("%s day%s" % (days, 's' if days > 1 else ''))    if hours:        currentTime.append("%s hour%s" % (hours, 's' if hours > 1 else ''))    if minutes:        currentTime.append("%s minute%s" % (minutes, 's' if minutes > 1 else ''))    if len(currentTime) == 1:        return currentTime[0]    if len(currentTime) == 2:        return currentTime[0] + " and " + currentTime[1]    return ", ".join(currentTime[:-1]) + " and " + currentTime[-1]