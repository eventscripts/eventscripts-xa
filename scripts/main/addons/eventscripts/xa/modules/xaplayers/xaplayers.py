import esimport xaimport xa.languageimport xa.loggingimport xa.settingimport playerlibimport popuplibimport servicesfrom xa import xa#plugin informationinfo = es.AddonInfo()info.name           = "Players"info.version        = "0.1"info.author         = "Hunter"info.url            = "http://forums.mattie.info"info.description    = "Clone of Mani Player Players feature for XA"info.tags           = "admin options players"manage_choice = {}manage_method = {}manage_display = {}manage_target = {}manage_pmenus = {}manage_argc = {}manage_cross_ref = {}xaplayers                   = xa.register('xaplayers')xalanguage                  = xa.language.getLanguage(xaplayers)xa_adminkick_anonymous      = xa.setting.createVariable(xaplayers, 'adminkick_anonymous', 0)xa_adminban_anonymous       = xa.setting.createVariable(xaplayers, 'adminban_anonymous', 0)xa_ban_time                 = xa.setting.createVariable(xaplayers, 'ban_time', 0)def load():    #Load Function for Player Settings for XA.    xaplayermenu = popuplib.easymenu("xaplayermenu", "_tempcore", _select_option)    xaplayermenu.settitle(xalanguage["choose option"])    xaplayers.addMenu("xaplayermenu", xalanguage["manage players"], "xaplayermenu", "manage_player", "#admin")        xaplayertargetmenu = popuplib.easymenu("xaplayertargetmenu", "_tempcore", _select_target)    xaplayertargetmenu.settitle(xalanguage["choose target"])    xaplayertargetmenu.addoption("player", xalanguage["select a player"])    xaplayertargetmenu.addoption("team3", xalanguage["counter terrorists"])    xaplayertargetmenu.addoption("team2", xalanguage["terrorists"])    xaplayertargetmenu.addoption("all", xalanguage["all players"])        registerOption("kick", xalanguage["kick"], _manage_kick, 1)    registerOption("ban", xalanguage["ban"], _manage_ban, 1)def unload():    for manage in manage_method:        unRegisterOption(manage)    popuplib.delete("xaplayermenu")    popuplib.delete("xaplayertargetmenu")    for page in manage_pmenus:        page.delete()    xa.unRegister(xaplayers)    def _select_option(userid, choice, name):    manage_choice[userid] = choice    if not userid in manage_target:        popuplib.send("xaplayertargetmenu", userid)    else:        _manage_player(manage_target[userid], manage_choice[userid], userid)        del manage_target[userid]    def _select_target(userid, choice, name):    if choice == "player":        if userid in manage_pmenus:            manage_pmenus[userid].delete()        manage_pmenus[userid] = popuplib.construct("xamanageplayermenu"+str(userid), "players", "#all")        manage_pmenus[userid].settitle(xalanguage["choose player"])        manage_pmenus[userid].menuselectfb = _select_player        manage_pmenus[userid].send(userid)    else:        if choice == "team3":            playerlist = playerlib.getUseridList("#ct")        elif choice == "team2":            playerlist = playerlib.getUseridList("#t")        elif choice == "all":            playerlist = es.getUseridList()        for player in playerlist:            _manage_player(player, manage_choice[userid], userid)            def _select_player(userid, choice, name):    _manage_player(choice, manage_choice[userid], userid)    def _command_player():    adminid = es.getcmduserid()    if adminid > 0:        admin = playerlib.getPlayer(adminid)    cmd = es.getargv(0).replace('ma_', 'xa_')    if cmd in manage_cross_ref:        option = manage_cross_ref[cmd]        if option in manage_argc:            argc = es.getargc()            if argc > manage_argc[option]:                args = []                for i in range(1, argc):                    args.append(es.getargv(i))                user = es.getargv(1)                for userid in playerlib.getUseridList(user):                    _manage_player(userid, option, adminid, args)            elif adminid > 0:                es.tell(adminid, xalanguage("not enough args", (), admin.get("lang")))            else:                es.dbgmsg(0, xalanguage("not enough args"))def _manage_player(userid, option, adminid, args = []):    auth = services.use("auth")    if (adminid == 0) or auth.isUseridAuthorized(adminid, option+"_player"):        if callable(manage_method[option]):            xa.logging.log(xaplayers, "Admin "+str(adminid)+ " used option "+str(option)+" on player "+str(userid))            manage_method[option](userid, adminid, args)        else:            es.dbgmsg(0, "xaplayers.py: Cannot find method '"+str(manage_method[option])+"'!")    else:        es.tell(adminid, xalanguage("not allowed", (), playerlib.getPlayer(adminid).get("lang")))def registerOption(option, name, method, argc = 0):    if not option in manage_method:        manage_method[option] = method        manage_display[option] = name        manage_argc[option] = argc        manage_cross_ref['xa_'+option] = option        xaplayermenu = popuplib.find("xaplayermenu")        xaplayermenu.addoption(option, name, 1)        if manage_argc[option] > 0:            xaplayers.addCommand('xa_'+option, _command_player, option+"_player", "#admin").register(('say', 'console','server'))        return True    else:        return False    def unRegisterOption(option):    if option in manage_method:        xaplayermenu = popuplib.find("xaplayermenu")        xaplayermenu.addoption(option, manage_display[option], 0)        if manage_argc[option] > 0:            xaplayers.delCommand('xa_'+option)        manage_method[option] = None        del manage_display[option]        del manage_argc[option]        del manage_cross_ref['xa_'+option]        return True    else:        return False        def managePlayer(option, userid, adminid):    if option in manage_method:        _manage_player(userid, option, adminid)        return True    else:        return Falsedef sendPlayersMenu(userid, victimid):    for user in list(userid):        manage_target[user] = victimid        xaplayermenu.send(user)# The default options that ship with the moduledef _manage_kick(userid, adminid, args):    if str(xa_adminkick_anonymous) == '0':        tokens = {}        tokens['admin']   = es.getplayername(adminid)        tokens['user']    = es.getplayername(userid)        for user in playerlib.getPlayerList():            es.tell(user, xalanguage("admin kick", tokens, user.get("lang")))    es.server.cmd("kickid "+str(userid)+" Kicked by Admin")def _manage_ban(userid, adminid, args):    if len(args) > 1:        bantime = args[1]    else:        bantime = xa_ban_time    if str(xa_adminban_anonymous) == '0':        tokens = {}        tokens['admin']   = es.getplayername(adminid)        tokens['user']    = es.getplayername(userid)        for user in playerlib.getPlayerList():            if int(bantime) > 0:                tokens['time']    = xalanguage("bantime", {'min': str(bantime)}, user.get("lang"))            else:                tokens['time']    = xalanguage("banperm", {}, user.get("lang"))            es.tell(user, xalanguage("admin ban", tokens, user.get("lang")))    es.server.cmd("banid "+str(bantime)+" "+str(userid)+" kick")