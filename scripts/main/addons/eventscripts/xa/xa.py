#import EventScripts
import es

#begin loading
es.dbgmsg(0, "[eXtensible Admin] Begin loading...")

#import custom stuff
import os
import hotshot
import services
import gamethread
import playerlib
import popuplib
import keymenulib
import settinglib
import keyvalues
from hotshot import stats
from os import getcwd

#helper variables
gAddonDir = str(es.server_var["eventscripts_addondir"]).replace("\\", "/")
gGameDir = str(es.server_var["eventscripts_gamedir"]).replace("\\", "/")

#import libraries
import configparser
import language
import logging
import playerdata
import setting

#import compiler
import psyco
psyco.full()

#plugin information
info = es.AddonInfo()
info.name = "eXtensible Admin EventScripts Python addon"
info.version = "0.7.0.317"
info.author = "EventScripts Developers"
info.url = "http://forums.mattie.info/cs/forums/viewforum.php?f=97"
info.description = "eXtensible Admin EventScripts Python addon"
info.basename = "xa"

##################### ######################################################
#Variables Section# # PLEASE KEEP IN MIND THAT THOSE VARIABLES ARE PRIVATE #
##################### ######################################################
##generate import dict
gImportLibraries = dir()
## list of core variables
gCoreVariables = []
## language strings
gLanguage = language.getLanguage()
## Version variable
gVersion = es.ServerVar("eventscripts_xa", str(info.version), "eXtensible Admin Version")
gVersion.makepublic()
## is server logging enabled?
gLog = es.ServerVar("xa_log", 0, "Activates the module logging")
gCoreVariables.append(gLog)
## is XA debugging enabled?
gDebug = es.ServerVar("xa_debug", 0, "Activates the module/library debugging")
gCoreVariables.append(gDebug)
## is XA profiling enabled?
gDebugProfile = es.ServerVar("xa_debugprofile", 0, "Activates the module/library profiling")
gCoreVariables.append(gDebugProfile)
## is Mani compatibility enabled?
gManiMode = es.ServerVar("xa_manimode", 0, "Is Mani compatibility mode active?")
gCoreVariables.append(gManiMode)
## whats the say command prefix?
gSayPrefix = es.ServerVar("xa_sayprefix", "!", "Say command prefix")
gCoreVariables.append(gSayPrefix)
## gMainMenu/gMainCommand/gMainCommandAlternative holds XAs main menu/main command
gMainMenu = {}
gMainCommand = None
gMainCommandAlternative = None
## gModules holds all the modules
gModules = {}
## gCommands holds all the information for commands
gCommands = {}
gCommands['perm'] = {}
gCommands['block'] = {}
gCommands['chat'] = {}
## gMenus holds all the information for menus
gMenus = {}
gMenus['perm'] = {}
gMenus['page'] = {}
gMenus['text'] = {}

#################### ######################################################
#Core Class Section# # PLEASE KEEP IN MIND THAT THOSE CLASSES ARE PRIVATE #
#################### ######################################################
## Library API
# Admin_libfunc is a 'fake' method class used for the lib API
class Admin_libfunc(object):
    def __init__(self, gLib, gFunc, gModule):
        self._xalib = gLib
        self._xalibfunc = gFunc
        self._xalibfunccalls = 0
        self._xalibfuncstats = {'calls':0, 'times':0}
        self._xamod = gModule
    def __call__(self, *args, **kw):
        self._xalibfunccalls += 1
        if int(gDebug) >= 1 or int(gDebugProfile) > 0: #check debug here to be faster
            fn = '%s/xa.prof' % es.getAddonPath('xa')
            pr = hotshot.Profile(fn)
            re = pr.runcall(self._xalibfunc, *(self._xamod,)+args, **kw)
            pr.close()
            st = stats.load(fn)
            st.strip_dirs()
            st.sort_stats('time', 'calls')
            if int(gDebug) >= 2:
                es.dbgmsg(0, '--------------------')
                es.dbgmsg(0, ('Admin_libfunc %d: __call__(%s.%s [%s], %s, %s)' % (self._xalibfunccalls, str(self._xalib.__name__), str(self._xalibfunc.__name__), str(self._xamod), args, kw)))
                es.dbgmsg(0, ('Admin_libfunc %d: Profile Statistics' % (self._xalibfunccalls)))
                st.print_stats(20)
                es.dbgmsg(0, '--------------------')
            elif int(gDebug) == 1:
                es.dbgmsg(0, ('Admin_libfunc %d: __call__(%s.%s [%s], %s, %s)' % (self._xalibfunccalls, str(self._xalib.__name__), str(self._xalibfunc.__name__), str(self._xamod), args, kw)))
                es.dbgmsg(0, ('Admin_libfunc %d: %d calls in %f CPU seconds' % (self._xalibfunccalls, st.total_calls, st.total_tt)))
            if int(gDebugProfile) > 0:
                self._xalibfuncstats['calls'] += st.total_calls
                self._xalibfuncstats['times'] += st.total_tt
            if os.path.exists(fn):
                os.unlink(fn)
            return re
        else:
            return self._xalibfunc(self._xamod, *args, **kw)

# Admin_lib is a 'fake' library class used for the lib API
class Admin_lib(object):
    def __init__(self, gLib, gModule):
        self._xalib = gLib
        self._xalibcalls = 0
        self._xalibfuncs = {}
        self._xamod = gModule
    def __getattr__(self, name):
        self._xalibcalls += 1
        if int(gDebug) >= 2: #check debug here to be faster
            es.dbgmsg(0, ('Admin_lib %d: __getattr__(%s [%s], %s)' % (self._xalibcalls, str(self._xalib.__name__), str(self._xamod), name)))
        if self._xalib.__dict__.has_key(name) and not name.startswith('_'):
            if not name in self._xalibfuncs:
                self._xalibfuncs[name] = Admin_libfunc(self._xalib, self._xalib.__dict__[name], self._xamod)
            return self._xalibfuncs[name]
        else:
            raise AttributeError

## Core
# Admin_module is the module class
class Admin_module(object):
    # XA reference, lookup once, required in all instances:
    _xa = None
    # methods:
    def __init__(self, gModule):
        #initialization of the module
        self._xamod = None
        self._xalibs = {}
        self.name = gModule
        self.allowAutoUnload = True
        self.subCommands = {}
        self.subMenus = {}
        self.customPermissions = {}
        self.requiredFrom = []
        self.requiredList = []
        self.variables = {}
        es.dbgmsg(0, "[eXtensible Admin] Registered module \""+self.name+"\"")
    def __getattr__(self, name):
        if not self._xa:
            for mod in es.addons.getAddonList():
                if mod.__name__ == 'xa.xa':
                    self._xa = mod
        if (name in gImportLibraries) and (self._xa.__dict__.has_key(name)):
            if not name in self._xalibs:
                self._xalibs[name] = Admin_lib(self._xa.__dict__[name], self)
            return self._xalibs[name]
        else:
            raise AttributeError
    def __str__(self):
        return self.name
    def getModule(self):
        if not self._xamod:
            for mod in es.addons.getAddonList():
                if mod.__name__ == 'xa.xa.modules.'+self.name:
                    self._xamod = mod
        return self._xamod
    def delete(self):
        unRegister(self.name)
    def unregister(self):
        unregister(self.name)
    def unRegister(self):
        unregister(self.name)
    def addRequirement(self, gModuleList):
        fails = 0
        if isinstance(gModuleList, str):
            modules = [gModuleList]
        else:
            modules = list(gModuleList)
        for module in modules:
            if module in gModules:
                m = gModules[module]
                m.requiredFrom.append(self.name)
                self.requiredList.append(m.name)
            else:
                fails += 1
        if fails > 0:
            return False
        else:
            return True
    def delRequirement(self, gModuleList):
        fails = 0
        if isinstance(gModuleList, str):
            modules = [gModuleList]
        else:
            modules = list(gModuleList)
        for module in modules:
            if (module in self.requiredList) and (module in gModules):
                m = gModules[module]
                m.requiredFrom.remove(self.name)
                self.requiredList.remove(m.name)
            else:
                fails += 1
        if fails > 0:
            return False
        else:
            return True
    def addCommand(self, command, block, perm, permlvl, descr="eXtensible Admin command", mani=False):
        #create new menu
        self.subCommands[command] = Admin_command(command, block, perm, self.getLevel(permlvl), descr, mani)
        return self.subCommands[command]
    def delCommand(self, command):
        #delete a menu
        if (command in self.subCommands):
            if self.subCommands[command]:
                self.subCommands[command].unregister(['server','console','say'])
                self.subCommands[command] = None
        else:
            es.dbgmsg(0,"Xa.py: Cannot delete menu \""+menu+"\", it does not exist")
    def isCommand(self, command):
        if (command in self.subCommands):
            return True
        return False
    def findCommand(self, command):
        if (command in self.subCommands):
            return self.subCommands[command]
        return None
    def addMenu(self, menu, display, menuname, perm, permlvl):
        #create new menu
        self.subMenus[menu] = Admin_menu(menu, display, menuname, perm, self.getLevel(permlvl))
        return self.subMenus[menu]
    def delMenu(self, menu):
        #delete a menu
        if (menu in self.subMenus):
            if self.subMenus[menu]:
                self.subMenus[menu].unregister()
                self.subMenus[menu] = None
        else:
            es.dbgmsg(0,"Xa.py: Cannot delete menu \""+menu+"\", it does not exist")
    def isMenu(self, menu):
        if (menu in self.subMenus):
            return True
        return False
    def findMenu(self, menu):
        if (menu in self.subMenus):
            return self.subMenus[menu]
        return None
    def getLevel(self, permlvl):
        try:
            level = int(permlvl)
        except ValueError:
            auth = services.use("auth")
            if permlvl.upper() == '#ROOT':
                level = auth.ROOT
            elif permlvl.upper() == '#ADMIN':
                level = auth.ADMIN
            elif permlvl.upper() == '#POWERUSER':
                level = auth.POWERUSER
            elif permlvl.upper() == '#IDENTIFIED' or permlvl.upper() == "#KNOWN":
                level = auth.IDENTIFIED
            elif permlvl.upper() == '#UNRESTRICTED' or permlvl.upper() == "#ALL":
                level = auth.UNRESTRICTED
            else:
                level = None
        return level
    def registerCapability(self, perm, permlvl, permtype='admin'):
        permlvl = self.getLevel(permlvl)
        auth = services.use("auth")
        auth.registerCapability(perm, permlvl)
        self.customPermissions[perm] = {'level':permlvl, 'type':str(permtype).lower()}
        return None
    def isUseridAuthorized(self, userid, perm):
        auth = services.use("auth")
        return auth.isUseridAuthorized(userid, perm)
    def information(self, listlevel):
        if listlevel >= 1:
            es.dbgmsg(0, " ")
        es.dbgmsg(0, self.name)
        if listlevel >= 1:
            es.dbgmsg(0, "  Auto-Unload:  "+str(self.allowAutoUnload))
        if listlevel >= 2:
            es.dbgmsg(0, "  Required by:  "+str(len(self.requiredFrom)))
            for module in self.requiredFrom:
                es.dbgmsg(0,"    "+module)
            es.dbgmsg(0, "  Requires:     "+str(len(self.requiredList)))
            for module in self.requiredList:
                es.dbgmsg(0,"    "+module)
            es.dbgmsg(0, "  ")
            es.dbgmsg(0, "  Variables:    "+str(len(self.variables)))
            for var in self.variables:
                es.dbgmsg(0,"    "+var)
        if listlevel >= 3:
            es.dbgmsg(0, "  ")
            es.dbgmsg(0, "  Libs & Funcs: "+str(len(self._xalibs)))
            for lib in self._xalibs:
                es.dbgmsg(0,"    "+lib+" ["+str(self._xalibs[lib]._xalibcalls)+" calls]")
                for func in self._xalibs[lib]._xalibfuncs:
                    if self._xalibs[lib]._xalibfuncs[func]._xalibfuncstats['calls'] > 0:
                        es.dbgmsg(0,"        "+func+" ["+str(self._xalibs[lib]._xalibfuncs[func]._xalibfunccalls)+" calls, "+str(self._xalibs[lib]._xalibfuncs[func]._xalibfuncstats['calls'])+" subcalls, "+str(self._xalibs[lib]._xalibfuncs[func]._xalibfuncstats['times'])+" CPU seconds]")
                    else:
                        es.dbgmsg(0,"        "+func+" ["+str(self._xalibs[lib]._xalibfuncs[func]._xalibfunccalls)+" calls]")
            es.dbgmsg(0, "  -------------")

# Admin_command is the clientcmd class
class Admin_command(object):
    def __init__(self, gCommand, gBlock, gPerm, gPermLevel, gDescription="eXtensible Admin command", gManiComp=False):
        #initialization of the module
        self.name = gCommand
        self.block = gBlock
        self.permission = gPerm
        self.permissionlevel = gPermLevel
        self.manicomp = gManiComp
        self.descr = gDescription
        self.server = False
        self.console = False
        self.say = False
        self.chat = False
        if not isinstance(self.permissionlevel, int):
            es.dbgmsg(0, "[eXtensible Admin] Invalid default permission \""+str(gPermLevel)+"\"")
        gCommands['perm'][self.name] = self.permission
        gCommands['block'][self.name] = self.block
        gCommands['chat'][self.name] = self.chat
        services.use("auth").registerCapability(self.permission, self.permissionlevel)
    def __str__(self):
        return self.name
    def register(self, gList):
        if isinstance(gList, str):
            cmdlist = [gList]
        else:
            cmdlist = list(gList)
        if "server" in cmdlist and self.server == False:
            es.regcmd(self.name, "xa/incoming_server", self.descr)
            if self.manicomp and isManiMode() and self.name.startswith('xa_'):
                es.regcmd('ma_'+self.name[3:], "xa/incoming_server", self.descr)
            self.server = True
        if "console" in cmdlist and self.console == False:
            es.regclientcmd(self.name, "xa/incoming_console", self.descr)
            if self.manicomp and isManiMode() and self.name.startswith('xa_'):
                es.regclientcmd('ma_'+self.name[3:], "xa/incoming_console", self.descr)
            self.console = True
        if "say" in cmdlist and self.say == False:
            if self.name.startswith('xa_'):
                es.regsaycmd(str(gSayPrefix)+self.name[3:], "xa/incoming_say", self.descr)
            es.regsaycmd(self.name, "xa/incoming_say", self.descr)
            self.say = True
        if "chat" in cmdlist and self.chat == False:
            gCommands['chat'][self.name] = True
            self.chat = True
    def unregister(self, gList):
        if isinstance(gList, str):
            cmdlist = [gList]
        else:
            cmdlist = list(gList)
        if "console" in cmdlist and self.console == True:
            es.unregclientcmd(self.name)
            if self.manicomp and es.exists('command', 'ma_'+self.name[3:]) and self.name.startswith('xa_'):
                es.unregclientcmd('ma_'+self.name[3:])
            self.console = False
        if "say" in cmdlist and self.say == True:
            if self.name.startswith('xa_'):
                es.unregsaycmd(str(gSayPrefix)+self.name[3:])
            es.unregsaycmd(self.name)
            self.say = False
        if "chat" in cmdlist and self.chat == True:
            gCommands['chat'][self.name] = False
            self.chat = False
    def unRegister(self, gList):
        self.unregister(gList)
    def information(self, listlevel):
        if listlevel >= 1:
            es.dbgmsg(0, " ")
        es.dbgmsg(0, self.name)
        if listlevel >= 1:
            es.dbgmsg(0, "  Block:        "+str(self.block))
            es.dbgmsg(0, "  Server cmd:   "+str(self.server))
            es.dbgmsg(0, "  Console cmd:  "+str(self.console))
            es.dbgmsg(0, "  Say cmd:      "+str(self.say))
            es.dbgmsg(0, "  Chat cmd:     "+str(self.chat))
            es.dbgmsg(0, "  Mani cmd:     "+str(self.manicomp))
            es.dbgmsg(0, "  Permission:   "+str(self.permission))
            es.dbgmsg(0, "  Perm-level:   "+str(self.permissionlevel))
            es.dbgmsg(0, "  Description:  "+str(self.descr))

# Admin_menu is the clientcmd class
class Admin_menu(object):
    def __init__(self, gMenu, gDisplay, gMenuName, gPerm, gPermLevel):
        #initialization of the module
        self.name = gMenu
        self.display = gDisplay
        self.menu = gMenuName
        self.menutype = ""
        self.menuobj = None
        self.permission = gPerm
        self.permissionlevel = gPermLevel
        if popuplib.exists(self.menu):
            self.menutype = "popup"
            self.menuobj = popuplib.find(self.menu)
        elif keymenulib.exists(self.menu):
            self.menutype = "keymenu"
            self.menuobj = keymenulib.find(self.menu)
        elif settinglib.exists(self.menu):
            self.menutype = "setting"
            self.menuobj = settinglib.find(self.menu)
        gMenus['text'][self.name] = self.display
        if not isinstance(self.permissionlevel, int):
            es.dbgmsg(0, "[eXtensible Admin] Invalid default permission \""+str(gPermLevel)+"\"")
        gMenus['perm'][self.name] = self.permission
        gMenus['page'][self.name] = self.menuobj
        services.use("auth").registerCapability(self.permission, self.permissionlevel)
    def __str__(self):
        return self.name
    def unregister(self):
        if self.name in gMenus['page']:
            del gMenus['perm'][self.name]
            del gMenus['page'][self.name]
            del gMenus['text'][self.name]
    def unRegister(self):
        self.unregister()
    def setDisplay(self, display):
        self.display = display
        gMenus['text'][self.name] = self.display
        return True
    def setMenu(self, menu):
        if popuplib.exists(menu):
            self.menu = menu
            self.menutype = "popup"
            self.menuobj = popuplib.find(self.menu)
            gMenus['page'][self.name] = self.menuobj
            return True
        elif keymenulib.exists(menu):
            self.menu = menu
            self.menutype = "keymenu"
            self.menuobj = keymenulib.find(self.menu)
            gMenus['page'][self.name] = self.menuobj
            return True
        elif settinglib.exists(menu):
            self.menu = menu
            self.menutype = "setting"
            self.menuobj = settinglib.find(self.menu)
            gMenus['page'][self.name] = self.menuobj
            return True
        return False
    def information(self, listlevel):
        if listlevel >= 1:
            es.dbgmsg(0, " ")
        es.dbgmsg(0, self.name)
        if listlevel >= 1:
            es.dbgmsg(0, "  Display:      "+str(self.display))
            es.dbgmsg(0, "  Menuname:     "+str(self.menu))
            es.dbgmsg(0, "  Menutype:     "+str(self.menutype))
            es.dbgmsg(0, "  Permission:   "+str(self.permission))
            es.dbgmsg(0, "  Perm-level:   "+str(self.permissionlevel))

###########################
#Module methods start here#
###########################
def xa_load(pModuleid):
    es.load("xa/modules/"+pModuleid)

def xa_unload(pModuleid):
    es.unload("xa/modules/"+pModuleid)
    
def xa_reload(pModuleid):
    xa_unload(pModuleid)
    gamethread.delayed(0.1, xa_load, (pModuleid,))
    
def xa_runconfig():
    es.server.cmd("exec xamodules.cfg")
    
def xa_exec(pModuleid = None): # be backwards compatible, but just execute general module config
    xa_runconfig()
    
def debug(dbglvl, message):
    if int(gDebug) >= dbglvl:
        es.dbgmsg(0, message)

def register(pModuleid):
    #create new module
    gModules[pModuleid] = Admin_module(pModuleid)
    return gModules[pModuleid]

def unRegister(pModuleid):
    unregister(pModuleid)

def unregister(pModuleid):
    #delete a module
    pModuleid = str(pModuleid)
    if (pModuleid in gModules):
        if len(gModules[pModuleid].requiredFrom) > 0:
            es.dbgmsg(0, "[eXtensible Admin] ***********************************")
            es.dbgmsg(0, "[eXtensible Admin] WARNING! Module \""+gModules[pModuleid].name+"\" is required by "+str(len(gModules[pModuleid].requiredFrom)))
            for module in gModules[pModuleid].requiredFrom:
                if module in gModules:
                    es.dbgmsg(0, "[eXtensible Admin] Required by \""+module+"\"")
                else:
                    gModules[pModuleid].requiredFrom.remove(module)
            es.dbgmsg(0, "[eXtensible Admin] ***********************************")
        for module in gModules[pModuleid].requiredList:
            if module in gModules:
                gModules[module].requiredFrom.remove(gModules[pModuleid].name)
                gModules[pModuleid].requiredList.remove(module)
        for command in gModules[pModuleid].subCommands:
            gModules[pModuleid].delCommand(command)
        for menu in gModules[pModuleid].subMenus:
            gModules[pModuleid].delMenu(menu)
        es.dbgmsg(0, "[eXtensible Admin] Unregistered module \""+gModules[pModuleid].name+"\"")
        del gModules[pModuleid]
    else:
        es.dbgmsg(0,"Xa.py: Cannot unregister module \""+pModuleid+"\", it is not registered")

def exists(pModuleid):
    #does named module exist
    return (pModuleid in gModules)

def isRegistered(pModuleid):
    #does named module exist
    return (pModuleid in gModules)

def isRequired(pModuleid):
    #does named module exist and is required
    if (pModuleid in gModules):
        return bool(len(gModules[pModuleid].requiredFrom))
    return False

def find(pModuleid):
    #return class instance of named module
    if (pModuleid in gModules):
        return gModules[pModuleid]
    return None

def findMenu(pModuleid, pMenuid):
    #return class instance of named menu inside a module
    if (pModuleid in gModules):
        if (pMenuid in gModules[pModuleid].subMenus):
            return gModules[pModuleid].subMenus[pMenuid]
    return None

def findCommand(pModuleid, pCommandid):
    #return class instance of named menu inside a module
    if (pModuleid in gModules):
        if (pCommandid in gModules[pModuleid].subCommands):
            return gModules[pModuleid].subCommands[pCommandid]
    return None

def isManiMode():
    if str(gManiMode) == '0':
        return False
    else:
        return True

def sendMenu(userid=None):
    #send the XA main menu to a player
    if userid:
        userid = int(userid)
    elif es.getcmduserid():
        userid = int(es.getcmduserid())
    if userid and (es.exists("userid", userid)):
        gMainMenu[userid] = popuplib.easymenu("_xa_mainmenu_"+str(userid), None, incoming_menu)
        gMainMenu[userid].settitle(gLanguage["eXtensible Admin"])
        for page in gMenus['text']:
            if gMenus['perm'][page]:
                perm = gMenus['perm'][page]
                if services.use("auth").isUseridAuthorized(userid, perm):
                    gMainMenu[userid].addoption(page, gMenus['text'][page], 1)
        if popuplib.isqueued(gMainMenu[userid].name, userid):
            gMainMenu[userid].update(userid)
        else:
            gMainMenu[userid].send(userid)

##############################################
#Mani compatibility helper methods start here#
##############################################
class Admin_mani(object):
    def loadModules(self):
        filename = "%s/%s" % (es.getAddonPath('xa'), 'static/manimodule.txt')
        if os.path.exists(filename):
            f = open(filename, "rU")
            try:
                for line in f:
                    linelist = map(str, line.strip().split("|", 3))
                    if linelist[0] == "*":
                        xa_load(linelist[1])
                    else:
                        variable = es.ServerVar(linelist[0], 0)
                        if linelist[2] == str(variable) or linelist[2] == "*":
                            if not es.exists("script", "xa/modules/"+linelist[2]):
                                xa_load(linelist[1])
                        elif linelist[3] != str(variable) or linelist[3] == "*":
                            if not es.exists("script", "xa/modules/"+linelist[2]):
                                xa_load(linelist[1])
            finally:
                f.close()
        else:
            raise IOError, "Could not find xa/static/manimodule.txt!"

    def loadVariables(self):
        filename = "%s/%s" % (es.getAddonPath('xa'), 'static/maniconfig.txt')
        if os.path.exists(filename):
            f = open(filename, "rU")
            try:
                for line in f:
                    linelist = map(str, line.strip().split("|", 2))
                    es.ServerVar(linelist[0], linelist[1], linelist[2])
            finally:
                f.close()
            return True
        else:
            raise IOError, "Could not find xa/static/maniconfig.txt!"
            
    def convertClients(self):
        auth = services.use('auth')
        if not auth.name in ('group_auth', 'basic_auth'):
            # Unsupported Auth Provider
            return False

        filename = "%s/%s" % (es.getAddonPath('xa'), 'static/manipermission.txt')
        if os.path.exists(filename):
            permissions = keyvalues.KeyValues(name="manipermission.txt")
            permissions.load(filename)
        else:
            raise IOError, "Could not find xa/static/manipermission.txt!"

        filename = "%s/%s" % (gGameDir, 'cfg/mani_admin_plugin/clients.txt')
        if os.path.exists(filename):
            clients = keyvalues.KeyValues(name="clients.txt")
            clients.load(filename)
        else:
            # Could not find cfg/mani_admin_plugin/clients.txt!
            return False

        if not "players" in clients:
            clients["players"] = keyvalues.KeyValues(name="players")
        if not "admingroups" in clients:
            clients["admingroups"] = keyvalues.KeyValues(name="admingroups")
        if not "immunitygroups" in clients:
            clients["immunitygroups"] = keyvalues.KeyValues(name="immunitygroups")

        if auth.name == 'basic_auth':
            es.dbgmsg(0, "[eXtensible Admin] Converting clients.txt to Basic Auth")
            adminlist = str(es.ServerVar('BASIC_AUTH_ADMIN_LIST'))
            for client in clients["players"]:
                if 'steam' in clients["players"][str(client)]:
                    if not clients["players"][str(client)]['steam'] in adminlist.split(';'):
                        adminlist += ';' + str(clients["players"][str(client)]['steam'])
                        es.dbgmsg(0, ("[eXtensible Admin] Added Admin: %s [%s]" % (str(client), str(clients["players"][str(client)]['steam']))))
            es.dbgmsg(0, "[eXtensible Admin] Finished Mani setup for Basic Auth")        
        elif auth.name == 'group_auth':
            es.dbgmsg(0, "[eXtensible Admin] Converting clients.txt to Group Auth")
            permcache = []
            commandqueue = []
            adminflags = {}
            immunityflags = {}
            if int(es.ServerVar('mani_reverse_admin_flags')):
                for module in sorted(gModules):
                    x = gModules[module]
                    for command in sorted(x.subCommands):
                        adminflags[str(x.subCommands[command].permission)] = 'ADMIN'
                    for menu in x.subMenus:
                        adminflags[str(x.subMenus[menu].permission)] = 'ADMIN'
                    for custom in x.customPermissions:
                        if x.customPermissions[str(custom)]['type'] == 'admin':
                            adminflags[str(custom)] = 'ADMIN'
            if int(es.ServerVar('mani_reverse_immunity_flags')):
                for module in sorted(gModules):
                    x = gModules[module]
                    for custom in x.customPermissions:
                        if x.customPermissions[str(custom)]['type'] == 'immunity':
                            immunityflags[str(custom)] = 'ADMIN'
            for perm in permissions['adminflags']:
                if not str(perm) in adminflags:
                    adminflags[str(perm)] = permissions['adminflags'][str(perm)]
            for perm in permissions['immunityflags']:
                if not str(perm) in immunityflags:
                    immunityflags[str(perm)] = permissions['immunityflags'][str(perm)]
            for group in clients["admingroups"]:
                if 'ADMIN' in clients["admingroups"][str(group)].upper().split(' '):
                    commandqueue.append('gauth group delete "Mani_%s"' % (str(group).replace(' ', '_')))
                    commandqueue.append('gauth group create "Mani_%s" %d' % (str(group).replace(' ', '_'), int(es.ServerVar('AUTHSERVICE_UNRESTRICTED'))))
                    if int(es.ServerVar('mani_reverse_admin_flags')):
                        for perm in adminflags:
                            if (adminflags[str(perm)] in clients["admingroups"][str(group)].split(' ')) or (str(adminflags[str(perm)]).upper() == 'ADMIN'):
                                if not str(perm) in permcache:
                                    permcache.append(str(perm))
                                    commandqueue.append('gauth power create "%s" %s' % (str(perm), str(es.ServerVar('AUTHSERVICE_ADMIN'))))
                                commandqueue.append('gauth power give "%s" "Mani_%s"' % (str(perm), str(group).replace(' ', '_')))
                    else:
                        for perm in adminflags:
                            if (not adminflags[str(perm)] in clients["admingroups"][str(group)].split(' ')) or (str(adminflags[str(perm)]).upper() == 'ADMIN'):
                                if not str(perm) in permcache:
                                    permcache.append(str(perm))
                                    commandqueue.append('gauth power create "%s" %s' % (str(perm), str(es.ServerVar('AUTHSERVICE_ADMIN'))))
                                commandqueue.append('gauth power give "%s" "Mani_%s"' % (str(perm), str(group).replace(' ', '_')))
            for group in clients["immunitygroups"]:
                if 'IMMUNITY' in clients["immunitygroups"][str(group)].upper().split(' '):
                    commandqueue.append('gauth group delete "Mani_%s"' % (str(group).replace(' ', '_')))
                    commandqueue.append('gauth group create "Mani_%s" %d' % (str(group).replace(' ', '_'), int(es.ServerVar('AUTHSERVICE_UNRESTRICTED'))))
                    if int(es.ServerVar('mani_reverse_immunity_flags')):
                        for perm in immunityflags:
                            if (immunityflags[str(perm)] in clients["immunitygroups"][str(group)].split(' ')) or (str(immunityflags[str(perm)]).upper() == 'IMMUNITY'):
                                if not str(perm) in permcache:
                                    permcache.append(str(perm))
                                    commandqueue.append('gauth power create "%s" %s' % (str(perm), str(es.ServerVar('AUTHSERVICE_ADMIN'))))
                                commandqueue.append('gauth power give "%s" "Mani_%s"' % (str(perm), str(group).replace(' ', '_')))
                    else:
                        for perm in immunityflags:
                            if (not immunityflags[str(perm)] in clients["immunitygroups"][str(group)].split(' ')) or (str(immunityflags[str(perm)]).upper() == 'IMMUNITY'):
                                if not str(perm) in permcache:
                                    permcache.append(str(perm))
                                    commandqueue.append('gauth power create "%s" %s' % (str(perm), str(es.ServerVar('AUTHSERVICE_ADMIN'))))
                                commandqueue.append('gauth power give "%s" "Mani_%s"' % (str(perm), str(group).replace(' ', '_')))
            for client in clients["players"]:
                if 'steam' in clients["players"][str(client)]:
                    commandqueue.append('gauth user create "%s" "%s"' % (str(client), str(clients["players"][str(client)]['steam'])))
                    es.dbgmsg(0, ("[eXtensible Admin] Added Client: %s [%s]" % (str(client), str(clients["players"][str(client)]['steam']))))
                    if 'admingroups' in clients["players"][str(client)]:
                        for group in clients["players"][str(client)]["admingroups"].split(';'):
                            commandqueue.append('gauth user join "%s" "Mani_%s"' % (str(client), str(group).replace(' ', '_')))
                    if 'immunitygroups' in clients["players"][str(client)]:
                        for group in clients["players"][str(client)]["immunitygroups"].split(';'):
                            commandqueue.append('gauth user join "%s" "Mani_%s"' % (str(client), str(group).replace(' ', '_')))
            for cmd in commandqueue:
                es.server.cmd(cmd)
            es.dbgmsg(0, "[eXtensible Admin] Finished Mani setup for Group Auth")

###########################################
#EventScripts events and blocks start here#
###########################################

def load():
    global gMainMenu, gMainCommand, gMainCommandAlternative
    es.dbgmsg(0, "[eXtensible Admin] Second loading part...")
    if not es.exists("command", "xa"):
        es.regcmd("xa", "xa/consolecmd", "Open the eXtensible Admin menu")
    if not incoming_chat in es.addons.SayListeners:
        es.addons.registerSayFilter(incoming_chat)
    gMainCommand = Admin_command("xa", sendMenu, "xa_menu", services.use("auth").UNRESTRICTED)
    gMainCommand.register(["console", "say"])
    gMainCommandAlternative = Admin_command("admin", sendMenu, "xa_menu", services.use("auth").UNRESTRICTED)
    gMainCommandAlternative.register(["console"])
    es.dbgmsg(0, "[eXtensible Admin] Executing xa.cfg...")
    es.server.cmd('exec xa.cfg')
    #Mani compatibility
    es.dbgmsg(0, "[eXtensible Admin] Mani mode enabled = "+str(isManiMode()))
    if isManiMode():
        ma = Admin_mani()
        es.dbgmsg(0, "[eXtensible Admin] Executing mani_server.cfg...")
        ma.loadVariables()  #setup basic mani variables
        es.server.cmd("exec mani_server.cfg")
        ma.loadModules()    #load the mani modules if needed
        ma.convertClients() #convert the clients.txt
    es.dbgmsg(0, "[eXtensible Admin] Executing xamodules.cfg...")
    es.server.cmd('exec xamodules.cfg')
    es.dbgmsg(0, "[eXtensible Admin] Updating xamodules.cfg...")
    setting.addVariables()
    es.dbgmsg(0, "[eXtensible Admin] Finished loading")

def unload():
    global gMainMenu, gMainCommand, gMainCommandAlternative
    es.dbgmsg(0, "[eXtensible Admin] Begin unloading...")
    for module in gModules:
        if gModules[module].allowAutoUnload == True:
            for command in gModules[module].subCommands:
                gModules[module].subCommands[command].unregister(['console', 'say'])
            for menu in gModules[module].subMenus:
                gModules[module].subMenus[menu].unregister()
            es.dbgmsg(0, "[eXtensible Admin] Unloading module \""+gModules[module].name+"\"")
            es.unload("xa/modules/"+gModules[module].name)
    for menu in gMainMenu:
        if popuplib.exists(str(menu)):
            menu.delete()
    if gMainCommand:
        gMainCommand.unregister(["console","say"])
        del gMainCommand
    if gMainCommandAlternative:
        gMainCommandAlternative.unregister(["console"])
        del gMainCommandAlternative
    if incoming_chat in es.addons.SayListeners:
        es.addons.unregisterSayFilter(incoming_chat)
    es.dbgmsg(0, "[eXtensible Admin] Finished unloading sequence")
    es.dbgmsg(0, "[eXtensible Admin] Modules will now unregister themself...")

def consolecmd():
    #Command from server console or non-python script
    subcmd = es.getargv(1).lower()
    seccmd = es.getargv(2).lower()
    xname = es.getargv(3)
    argc = es.getargc()
    if xname in gModules:
        x = gModules[xname]
    else:
        x = None
    if subcmd == "load":
        if es.getargv(2):
            xa_load(es.getargv(2))
        else:
            es.dbgmsg(0,"Syntax: xa load <module-name>")
    elif subcmd == "unload":
        if es.getargv(2):
            xa_unload(es.getargv(2))
        else:
            es.dbgmsg(0,"Syntax: xa unload <module-name>")
    elif subcmd == "reload":
        if es.getargv(2):
            xa_reload(es.getargv(2))
        else:
            es.dbgmsg(0,"Syntax: xa reload <module-name>")
    elif subcmd == "send":
        if es.getargv(2):
            sendMenu(es.getargv(2))
        else:
            es.dbgmsg(0,"Syntax: xa send <userid>")
    elif subcmd == "help":
        helplist = {}
        if seccmd and (str(seccmd) in gModules):
            x = gModules[str(seccmd)]
            for command in sorted(x.subCommands):
                helplist[str(command)] = ["cmd", str(x.subCommands[command].permission), str(x.subCommands[command].descr)]
            for variable in sorted(x.variables):
                helplist[str(variable)] = ["var", str(x.variables[variable]), str(x.variables[variable]._def), str(x.variables[variable]._descr)]
        else:
            for module in sorted(gModules):
                x = gModules[module]
                for command in sorted(x.subCommands):
                    helplist[str(command)] = ["cmd", str(x.subCommands[command].permission), str(x.subCommands[command].descr)]
                for variable in sorted(x.variables):
                    helplist[str(variable)] = ["var", str(x.variables[variable]), str(x.variables[variable]._def), str(x.variables[variable]._descr)]
        es.dbgmsg(0,"---------- List of commands and variables:")
        for helpindex in sorted(helplist):
            helpline = helplist[helpindex]
            if helpline[0] == "cmd":
                es.dbgmsg(0,("%-*s"%(40, helpindex))+" : "+("%-*s"%(8, "cmd"))+" : "+("%-*s"%(16, helpline[1]))+" : "+helpline[2])
            elif helpline[0] == "var":
                es.dbgmsg(0,("%-*s"%(40, helpindex))+" : "+("%-*s"%(8, helpline[1]))+" : "+("%-*s"%(16, helpline[2]))+" : "+helpline[3])
        es.dbgmsg(0,"----------")
        es.dbgmsg(0, "Syntax: xa help [module]")
    elif subcmd == "permissions":
        permissions = []
        if seccmd:
            userid = int(es.getuserid(seccmd))
        else:
            userid = None
        if userid:
            permissions.append(['Module', 'Permission', 'Level', 'Type', 'Name', 'Granted'])
        else:
            permissions.append(['Module', 'Permission', 'Level', 'Type', 'Name'])
        for module in sorted(gModules):
            x = gModules[module]
            if userid:
                for command in sorted(x.subCommands):
                    permissions.append([str(x.name), str(x.subCommands[command].permission), str(x.subCommands[command].permissionlevel), 'command', str(x.subCommands[command].name), x.isUseridAuthorized(userid, str(x.subCommands[command].permission))])
                for menu in x.subMenus:
                    permissions.append([str(x.name), str(x.subMenus[menu].permission), str(x.subMenus[menu].permissionlevel), 'menu', str(x.subMenus[menu].name), x.isUseridAuthorized(userid, str(x.subMenus[menu].permission))])
                for custom in x.customPermissions:
                    permissions.append([str(x.name), str(custom), str(x.customPermissions[custom]['level']), 'custom', str(x.customPermissions[custom]['type']), x.isUseridAuthorized(userid, str(custom))])
            else:
                for command in sorted(x.subCommands):
                    permissions.append([str(x.name), str(x.subCommands[command].permission), str(x.subCommands[command].permissionlevel), 'command', str(x.subCommands[command].name)])
                for menu in x.subMenus:
                    permissions.append([str(x.name), str(x.subMenus[menu].permission), str(x.subMenus[menu].permissionlevel), 'menu', str(x.subMenus[menu].name)])
                for custom in x.customPermissions:
                    permissions.append([str(x.name), str(custom), str(x.customPermissions[custom]['level']), 'custom', str(x.customPermissions[custom]['type'])])
        es.dbgmsg(0,"---------- List of permissions:")
        for perm in permissions:
            if userid:
                if not perm[5] == 'Granted':
                    if perm[5]:
                        granted = 'Yes'
                    else:
                        granted = 'No'
                else:
                    granted = perm[5]
                es.dbgmsg(0,("%-*s"%(18, perm[0]))+" "+("%-*s"%(20, perm[1]))+" "+("%-*s"%(8, "["+perm[2]+"]"))+" "+("%-*s"%(10, perm[3]))+" "+("%-*s"%(15, perm[4]))+" "+granted)
            else:
                es.dbgmsg(0,("%-*s"%(18, perm[0]))+" "+("%-*s"%(20, perm[1]))+" "+("%-*s"%(8, "["+perm[2]+"]"))+" "+("%-*s"%(10, perm[3]))+" "+perm[4])
        es.dbgmsg(0,"----------")
        es.dbgmsg(0, "Syntax: xa permissions [user]")
    elif subcmd == "stats":
        statistics = []
        for module in sorted(gModules):
            x = gModules[module]
            xlibs = 0
            xfuncs = 0
            xcalls = 0
            xsubcalls = 0
            xseconds = 0
            for lib in gModules[module]._xalibs:
                xlibs += 1
                for func in gModules[module]._xalibs[lib]._xalibfuncs:
                    xfuncs += 1
                    xcalls += gModules[module]._xalibs[lib]._xalibfuncs[func]._xalibfunccalls
                    xsubcalls += gModules[module]._xalibs[lib]._xalibfuncs[func]._xalibfuncstats['calls']
                    xseconds += gModules[module]._xalibs[lib]._xalibfuncs[func]._xalibfuncstats['times']
            statistics.append([str(x.name), xlibs, xfuncs, xcalls, xsubcalls, xseconds])
        es.dbgmsg(0,"---------- List of statistics:")
        if seccmd.isdigit():
            sortkey = int(seccmd)
        else:
            sortkey = 5
        if int(gDebugProfile) > 0:
            sortkey = min(5, sortkey)
        else:
            sortkey = min(3, sortkey)
        sortkey = max(0, sortkey)
        statistics = sorted(statistics, cmp=lambda x,y: cmp(x[sortkey], y[sortkey]))
        statistics.append(['Module', 'Libraries', 'Functions', 'Calls', 'SubCalls', 'CPU seconds'])
        if int(gDebugProfile) > 0:
            for stat in reversed(statistics):
                es.dbgmsg(0,("%-*s"%(18, stat[0]))+" "+("%-*s"%(10, str(stat[1])))+" "+("%-*s"%(10, str(stat[2])))+" "+("%-*s"%(10, str(stat[3])))+" "+("%-*s"%(10, str(stat[4])))+" "+str(stat[5]))
        else:
            for stat in reversed(statistics):
                es.dbgmsg(0,("%-*s"%(18, stat[0]))+" "+("%-*s"%(10, str(stat[1])))+" "+("%-*s"%(10, str(stat[2])))+" "+str(stat[3]))
        es.dbgmsg(0,"----------")
        es.dbgmsg(0, "Syntax: xa stats [sort-column]")
    elif subcmd == "module":
        if seccmd == "register":
            if xname:
                if x:
                    es.dbgmsg(0,"[eXtensible Admin] Could not register module \""+xname+"\", it is already registered")
                else:
                    register(xname)
            else:
                es.dbgmsg(0,"Syntax: xa module register <module-name>")
        elif seccmd == "unregister":
            if xname:
                if x:
                    unRegister(xname)
                else:
                    es.dbgmsg(0,"[eXtensible Admin] Could not unregister module \""+xname+"\", it is not registered")
            else:
                es.dbgmsg(0,"Syntax: xa module load <module-name>")
        elif seccmd == "exists":
            if argc >= 5:
                xname = es.getargv(3)
                retvar = es.getargv(4)
                es.set(retvar,int(exists(xname)))
            else:
                es.dbgmsg(0,"Syntax: xa module exists <module-name> <var>")
        elif seccmd == "isregistered":
            if argc >= 5:
                xname = es.getargv(3)
                retvar = es.getargv(4)
                es.set(retvar,int(isRegistered(xname)))
            else:
                es.dbgmsg(0,"Syntax: xa module isloaded <module-name> <var>")
        elif seccmd == "isrequired":
            if argc >= 5:
                xname = es.getargv(3)
                retvar = es.getargv(4)
                es.set(retvar,int(isRequired(xname)))
            else:
                es.dbgmsg(0,"Syntax: xa module isrequired <module-name> <var>")
        elif seccmd == "addrequirement":
            if xname and argc >= 5:
                if x:
                    result = x.addRequirement(es.getargv(4))
                    if result == True:
                        es.dbgmsg(0,"[eXtensible Admin] Added module \""+str(es.getargv(4))+"\" as a requirement for module \""+xname+"\"")
                    else:
                        es.dbgmsg(0,"[eXtensible Admin] Could not add modules as a requirement for module \""+xname+"\"")
                else:
                    es.dbgmsg(0,"[eXtensible Admin] The module \""+xname+"\" is not registered")
            else:
                es.dbgmsg(0,"Syntax: xa module addrequirement <module-name> <required-module>")
        elif seccmd == "delrequirement":
            if xname and argc >= 5:
                if x:
                    result = x.delRequirement(es.getargv(4))
                    if result == True:
                        es.dbgmsg(0,"[eXtensible Admin] Deleted module \""+str(es.getargv(4))+"\" as a requirement from module \""+xname+"\"")
                    else:
                        es.dbgmsg(0,"[eXtensible Admin] Could not delete modules as a requirement from module \""+xname+"\"")
                else:
                    es.dbgmsg(0,"[eXtensible Admin] The module \""+xname+"\" is not registered")
            else:
                es.dbgmsg(0,"Syntax: xa module delrequirement <module-name> <required-module>")
        elif seccmd == "list":
            es.dbgmsg(0,"---------- List of modules:")
            if argc == 3:
                listlevel = 0
            else:
                listlevel = int(xname)
            for module in gModules:
                x = gModules[module]
                x.information(listlevel)
            if argc == 3:
                es.dbgmsg(0, " ")
                es.dbgmsg(0, "For more details, supply list level (0-3):")
                es.dbgmsg(0, "Syntax: xa module list [level]")
            es.dbgmsg(0,"----------")
        elif seccmd == "info":
            if argc >= 4:
                if argc == 5:
                    listlevel = int(es.getargv(4))
                else:
                    listlevel = 2
                if x:
                    x.information(listlevel)
            else:
                es.dbgmsg(0, "Syntax: xa module info <module-name> [level]")
        else:
            es.dbgmsg(0,"Syntax: xa module <subcommand>")
    elif subcmd == "command":
        if xname and x:
            xcommand = x.findCommand(es.getargv(4))
            if seccmd == "create":
                if not xcommand and argc >= 8:
                    if x:
                        command = str(es.getargv(4))
                        block = str(es.getargv(5))
                        perm = str(es.getargv(6))
                        permlvl = str(es.getargv(7))
                        descr = str(es.getargv(8))
                        mani = bool(es.getargv(9))
                        x.addCommand(command, block, perm, permlvl, descr, mani)
                else:
                    es.dbgmsg(0,"Syntax: xa command create <module-name> <command-name> <block> <permission> <permission-level> [description] [mani compatible 0/1]")
            elif seccmd == "delete":
                if argc >= 5:
                    if xcommand:
                        x.delCommand(command)
                    else:
                        es.dbgmsg(0,"[eXtensible Admin] Could not delete the command \""+es.getargv(4)+"\", it does not exists")
                else:
                    es.dbgmsg(0,"Syntax: xa command delete <module-name> <command-name>")
            elif seccmd == "exists":
                if argc >= 6:
                    retvar = es.getargv(5)
                    es.set(retvar,int(x.isCommand(es.getargv(4))))
                else:
                    es.dbgmsg(0,"Syntax: xa command exists <module-name> <command-name> <var>")
            elif seccmd == "register":
                if argc >= 6:
                    if xcommand:
                        cmdtype = str(es.getargv(5))
                        xcommand.register(cmdtype)
                    else:
                        es.dbgmsg(0,"[eXtensible Admin] The command \""+es.getargv(4)+"\" does not exists")
                else:
                    es.dbgmsg(0,"Syntax: xa command register <module-name> <command-name> <server/console/say>")
            elif seccmd == "unregister":
                if argc >= 6:
                    if xcommand:
                        cmdtype = str(es.getargv(5))
                        xcommand.unRegister(cmdtype)
                    else:
                        es.dbgmsg(0,"[eXtensible Admin] The command \""+es.getargv(4)+"\" does not exists")
                else:
                    es.dbgmsg(0,"Syntax: xa command unregister <module-name> <command-name> <server/console/say>")
            elif seccmd == "list":
                es.dbgmsg(0,"---------- List of commands:")
                if argc == 4:
                    listlevel = 0
                else:
                    listlevel = int(es.getargv(4))
                for command in x.subCommands:
                    m = x.subCommands[command]
                    m.information(listlevel)
                if argc == 4:
                    es.dbgmsg(0, " ")
                    es.dbgmsg(0, "For more details, supply list level (0-1):")
                    es.dbgmsg(0, "Syntax: xa command list <module-name> [level]")
                es.dbgmsg(0,"----------")
            elif seccmd == "info":
                if argc >= 4:
                    m = x.findCommand(es.getargv(4))
                    if m:
                        m.information(1)
                    else:
                        es.dbgmsg(0,"[eXtensible Admin] The command \""+es.getargv(4)+"\" does not exists")
                else:
                    es.dbgmsg(0, "Syntax: xa command info <module-name> <command-name>")
            else:
                es.dbgmsg(0,"Syntax: xa command <module-name> <subcommand>")
        else:
            es.dbgmsg(0,"[eXtensible Admin] The module \""+xname+"\" is not registered")
            es.dbgmsg(0,"Syntax: xa command <module-name> <subcommand>")
    elif subcmd == "menu":
        if xname and x:
            xmenu = x.findMenu(es.getargv(4))
            if seccmd == "create":
                if not xmenu and argc >= 9:
                    if x:
                        menu = str(es.getargv(4))
                        display = str(es.getargv(5))
                        menuname = str(es.getargv(6))
                        perm = str(es.getargv(7))
                        permlvl = str(es.getargv(8))
                        x.addMenu(menu, display, menuname, perm, permlvl)
                else:
                    es.dbgmsg(0,"Syntax: xa menu create <module-name> <menu-name> <display-name> <popup/keymenu-name> <permission> <permission-level>")
            elif seccmd == "delete":
                if argc >= 5:
                    if xmenu:
                        x.delMenu(menu)
                    else:
                        es.dbgmsg(0,"[eXtensible Admin] Could not delete the menu \""+es.getargv(4)+"\", it does not exists")
                else:
                    es.dbgmsg(0,"Syntax: xa menu delete <module-name> <menu-name>")
            elif seccmd == "exists":
                if argc >= 6:
                    retvar = es.getargv(5)
                    es.set(retvar,int(x.isMenu(es.getargv(4))))
                else:
                    es.dbgmsg(0,"Syntax: xa menu exists <module-name> <menu-name> <var>")
            elif seccmd == "setdisplay":
                if argc >= 6:
                    if xmenu:
                        display = str(es.getargv(5))
                        xmenu.setDisplay(display)
                    else:
                        es.dbgmsg(0,"[eXtensible Admin] The menu \""+es.getargv(4)+"\" does not exists")
                else:
                    es.dbgmsg(0,"Syntax: xa menu setdisplay <module-name> <menu-name> <display-name>")
            elif seccmd == "setmenu":
                if argc >= 6:
                    if xmenu:
                        menuname = str(es.getargv(5))
                        if popuplib.exists(menuname) or keymenulib.exists(menuname):
                            xmenu.setMenu(menuname)
                        else:
                            es.dbgmsg(0,"[eXtensible Admin] There is no popup or keymenu named \""+menuname+"\"")
                    else:
                        es.dbgmsg(0,"[eXtensible Admin] The menu \""+es.getargv(4)+"\" does not exists")
                else:
                    es.dbgmsg(0,"Syntax: xa menu setmenu <module-name> <menu-name> <popup/keymenu-name>")
            elif seccmd == "list":
                es.dbgmsg(0,"---------- List of menus:")
                if argc == 4:
                    listlevel = 0
                else:
                    listlevel = int(es.getargv(4))
                for menu in x.subMenus:
                    m = x.subMenus[menu]
                    m.information(listlevel)
                if argc == 4:
                    es.dbgmsg(0, " ")
                    es.dbgmsg(0, "For more details, supply list level (0-1):")
                    es.dbgmsg(0, "Syntax: xa menu list <module-name> [level]")
                es.dbgmsg(0,"----------")
            elif seccmd == "info":
                if argc >= 4:
                    m = x.findMenu(es.getargv(4))
                    if m:
                        m.information(1)
                    else:
                        es.dbgmsg(0,"[eXtensible Admin] The menu \""+es.getargv(4)+"\" does not exists")
                else:
                    es.dbgmsg(0, "Syntax: xa menu info <module-name> <menu-name>")
            else:
                es.dbgmsg(0,"Syntax: xa menu <module-name> <subcommand>")
        else:
            es.dbgmsg(0,"[eXtensible Admin] The module \""+xname+"\" is not registered")
            es.dbgmsg(0,"Syntax: xa menu <module-name> <subcommand>")
    else:
        es.dbgmsg(0,"Invalid xa subcommand, see http://python.eventscripts.com/pages/XA for help")

#############################################
#EventScripts command/menu blocks start here#
#############################################

def incoming_server():
    command = es.getargv(0)
    if command.startswith('ma_'):
        command = 'xa_'+command[3:]
    if command in gCommands['perm']:
        block = gCommands['block'][command]
        if callable(block):
            try:
                block()
            except:
                pass
        else:
            es.doblock(block)

def incoming_console():
    userid = es.getcmduserid()
    command = es.getargv(0)
    if command.startswith('ma_'):
        command = 'xa_'+command[3:]
    if command in gCommands['perm']:
        if gCommands['perm'][command]:
            perm = gCommands['perm'][command]
            auth = services.use("auth")
            if auth.isUseridAuthorized(userid, perm):
                block = gCommands['block'][command]
                if callable(block):
                    try:
                        block()
                    except:
                        pass
                else:
                    es.doblock(block)

def incoming_say():
    userid = es.getcmduserid()
    command = es.getargv(0)
    if command.startswith('ma_'):
        command = 'xa_'+command[3:]
    elif command.startswith(str(gSayPrefix)):
        command = 'xa_'+command[len(str(gSayPrefix)):]
    if command in gCommands['perm']:
        if gCommands['perm'][command]:
            perm = gCommands['perm'][command]
            auth = services.use("auth")
            if auth.isUseridAuthorized(userid, perm):
                block = gCommands['block'][command]
                if callable(block):
                    try:
                        block()
                    except:
                        pass
                else:
                    es.doblock(block)
                    
def incoming_chat(userid, message, teamonly):
    output = message
    if output[0] == output[-1:] == '"':
        output = output[1:-1]
    command = output.split(' ')[0]
    if command.startswith('ma_'):
        command = 'xa_'+command[3:]
    elif command.startswith(str(gSayPrefix)):
        command = 'xa_'+command[len(str(gSayPrefix)):]
    if command in gCommands['chat']:
        if gCommands['chat'][command] and gCommands['perm'][command]:
            perm = gCommands['perm'][command]
            auth = services.use("auth")
            if auth.isUseridAuthorized(userid, perm):
                block = gCommands['block'][command]
                if callable(block):
                    try:
                        block()
                    except:
                        pass
                else:
                    es.doblock(block)
    return (userid, message, teamonly)

def incoming_menu(userid, choice, name):
    if choice in gMenus['perm']:
        if gMenus['perm'][choice]:
            perm = gMenus['perm'][choice]
            auth = services.use("auth")
            if auth.isUseridAuthorized(userid, perm):
                page = gMenus['page'][choice]
                page.send(userid)
