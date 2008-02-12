#import EventScripts
import es
import gamethread
from es import server_var

#load and import the core
es.dbgmsg(0, "[eXtensible Admin] Begin loading...")

#import custom stuff
import os
import services
import playerlib
import popuplib
import keymenulib
import settinglib
from os import getcwd

import configparser
import language
import logging
import playerdata
import setting
import manilib

import psyco
psyco.full()

#plugin information
info = es.AddonInfo()
info.name = "eXtensible Admin EventScripts Python addon"
info.version = "0.7.0"
info.author = "EventScripts Developers"
info.url = "http://forums.mattie.info/cs/forums/viewforum.php?f=93"
info.description = "eXtensible Admin EventScripts Python addon"
info.basename = "xa"

#global variables:
## list of core variables
gCoreVariables = []
## language strings
gLanguage = language.getLanguage()
## Version variable
gVersion = es.ServerVar("eventscripts_xa", "0.7.0.214", "eXtensible Admin Version")
gVersion.makepublic()
## is server logging enabled?
gLog = es.ServerVar("xa_log", 0, "Activates the module logging")
gCoreVariables.append(gLog)
## is Mani compatibility enabled?
gManiMode = es.ServerVar("xa_manimode", 0, "Is Mani compatibility mode active?")
gCoreVariables.append(gManiMode)
## gMainMenu/gMainCommand holds XAs main menu/main command
gMainMenu = {}
gMainCommand = None
## gModules holds all the modules
gModules = {}
## gCommandsPerm/Block holds all the permission/block names of commands
gCommandsPerm = {}
gCommandsBlock = {}
## gMenusPerm/Page holds all the permission/page names of menus
gMenusPerm = {}
gMenusPage = {}
gMenusText = {}

selfaddondir = str(es.server_var["eventscripts_addondir"]).replace("\\", "/")
selfmoddir = str(es.server_var["eventscripts_gamedir"]).replace("\\", "/")

#################### ######################################################
#Core Class Section# # PLEASE KEEP IN MIND THAT THOSE CLASSES ARE PRIVATE #
#################### ######################################################
# Admin_module is the module class
class Admin_module(object):
    def __init__(self, gModule):
        #initialization of the module
        self.name = gModule
        self.allowAutoUnload = True
        self.subCommands = {}
        self.subMenus = {}
        self.requiredFrom = []
        self.requiredList = []
        self.variables = {}
        es.dbgmsg(0, "[eXtensible Admin] Registered module \""+self.name+"\"")
    def __str__(self):
        return self.name
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
            if module in self.requiredList:
                m = gModules[module]
                m.requiredFrom.remove(self.name)
                self.requiredList.remove(m.name)
            else:
                fails += 1
        if fails > 0:
            return False
        else:
            return True
    def addCommand(self, command, block, perm, permlvl, target=False):
        #create new menu
        self.subCommands[command] = Admin_command(command, block, perm, permlvl, target)
        return self.subCommands[command]
    def delCommand(self, command):
        #delete a menu
        if (command in self.subCommands):
            self.subCommands[command].unRegister(['server','console','say'])
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
        self.subMenus[menu] = Admin_menu(menu, display, menuname, perm, permlvl)
        return self.subMenus[menu]
    def delMenu(self, menu):
        #delete a menu
        if (menu in self.subMenus):
            self.subMenus[menu].unRegister()
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
            es.dbgmsg(0, "  Variables:    "+str(len(self.variables)))
            for var in self.variables:
                es.dbgmsg(0,"    "+var)
            es.dbgmsg(0, "  Mani Vars:    "+str(len(self.variablesMani)))
            for var in self.variablesMani:
                es.dbgmsg(0,"    "+var)

# Admin_command is the clientcmd class
class Admin_command(object):
    def __init__(self, gCommand, gBlock, gPerm, gPermLevel, gTarget=False):
        #initialization of the module
        self.name = gCommand
        self.block = gBlock
        self.permission = gPerm
        self.permissionlevel = gPermLevel
        self.target = gTarget
        self.server = False
        self.console = False
        self.say = False
        auth = services.use("auth")
        if isinstance(gPermLevel, str):
            gPermLevel = gPermLevel.lower()
            if gPermLevel == "#root":
                self.permissionlevel = auth.ROOT
            elif gPermLevel == "#admin":
                self.permissionlevel = auth.ADMIN
            elif gPermLevel == "#poweruser":
                self.permissionlevel = auth.POWERUSER
            elif (gPermLevel == "#identified") or (gPermLevel == "#known"):
                self.permissionlevel = auth.IDENTIFIED
            elif (gPermLevel == "#unrestricted") or (gPermLevel == "#all"):
                self.permissionlevel = auth.UNRESTRICTED
        else:
            self.permissionlevel = int(gPermLevel)
        if not isinstance(self.permissionlevel, int):
            es.dbgmsg(0, "[eXtensible Admin] Invalid default permission \""+str(gPermLevel)+"\"")
        gCommandsPerm[self.name] = self.permission
        gCommandsBlock[self.name] = self.block
        auth.registerCapability(self.permission, self.permissionlevel)
    def __str__(self):
        return self.name
    def register(self, gList):
        if isinstance(gList, str):
            cmdlist = [gList]
        else:
            cmdlist = list(gList)
        if "server" in cmdlist and self.server == False:
            es.regcmd(self.name, "xa/incoming_server", "eXtensible Admin command")
            self.server = True
        if "console" in cmdlist and self.console == False:
            es.regclientcmd(self.name, "xa/incoming_console", "eXtensible Admin command")
            self.console = True
        if "say" in cmdlist and self.say == False:
            es.regsaycmd(self.name, "xa/incoming_say", "eXtensible Admin command")
            self.say = True
    def unregister(self, gList):
        if isinstance(gList, str):
            cmdlist = [gList]
        else:
            cmdlist = list(gList)
        if "console" in cmdlist and self.console == True:
            es.unregclientcmd(self.name)
            self.console = False
        if "say" in cmdlist and self.say == True:
            es.unregsaycmd(self.name)
            self.say = False
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
            es.dbgmsg(0, "  Target:       "+str(self.target))
            es.dbgmsg(0, "  Permission:   "+str(self.permission))
            es.dbgmsg(0, "  Perm-level:   "+str(self.permissionlevel))

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
        auth = services.use("auth")
        if popuplib.exists(self.menu):
            self.menutype = "popup"
            self.menuobj = popuplib.find(self.menu)
        elif keymenulib.exists(self.menu):
            self.menutype = "keymenu"
            self.menuobj = keymenulib.find(self.menu)
        elif settinglib.exists(self.menu):
            self.menutype = "setting"
            self.menuobj = settinglib.find(self.menu)
        gMenusText[self.name] = self.display
        if isinstance(gPermLevel, str):
            gPermLevel = gPermLevel.lower()
            if gPermLevel == "#root":
                self.permissionlevel = auth.ROOT
            elif gPermLevel == "#admin":
                self.permissionlevel = auth.ADMIN
            elif gPermLevel == "#poweruser":
                self.permissionlevel = auth.POWERUSER
            elif (gPermLevel == "#identified") or (gPermLevel == "#known"):
                self.permissionlevel = auth.IDENTIFIED
            elif (gPermLevel == "#unrestricted") or (gPermLevel == "#all"):
                self.permissionlevel = auth.UNRESTRICTED
        else:
            self.permissionlevel = int(gPermLevel)
        if not isinstance(self.permissionlevel, int):
            es.dbgmsg(0, "[eXtensible Admin] Invalid default permission \""+str(gPermLevel)+"\"")
        gMenusPerm[self.name] = self.permission
        gMenusPage[self.name] = self.menuobj
        auth.registerCapability(self.permission, self.permissionlevel)
    def __str__(self):
        return self.name
    def unregister(self):
        if self.name in gMenusPage:
            del gMenusPerm[self.name]
            del gMenusPage[self.name]
            del gMenusText[self.name]
    def unRegister(self):
        self.unregister()
    def setDisplay(self, display):
        self.display = display
        gMenusText[self.name] = self.display
        return True
    def setMenu(self, menu):
        if popuplib.exists(menu):
            self.menu = menu
            self.menutype = "popup"
            self.menuobj = popuplib.find(self.menu)
            gMenusPage[self.name] = self.menuobj
            return True
        elif keymenulib.exists(menu):
            self.menu = menu
            self.menutype = "keymenu"
            self.menuobj = keymenulib.find(self.menu)
            gMenusPage[self.name] = self.menuobj
            return True
        elif settinglib.exists(menu):
            self.menu = menu
            self.menutype = "setting"
            self.menuobj = settinglib.find(self.menu)
            gMenusPage[self.name] = self.menuobj
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

#basic commands begin here
#usage from other Python scripts for example:
#
# TODO:
# - Add all the module and command wrappers for the classes
# - The "incoming" functions for clientcmd's and servercmd's needs to be done (see the Admin_command class)
#
# The classes are hidden to the outer world. All other python modules use functions that are specified below!

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
    
def xa_exec(pModuleid):
    es.server.cmd("exec xa_"+pModuleid+".cfg")

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
            es.dbgmsg(0, "[eXtensible Admin] WARNING! Module \""+gModules[pModuleid].name+"\" is required by "+str(len(gModules[pModuleid].requiredFrom)))
            for module in gModules[pModuleid].requiredFrom:
                if module in gModules:
                    es.dbgmsg(0, "[eXtensible Admin]  \""+module+"\"")
                else:
                    gModules[pModuleid].requiredFrom.remove(module)
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
        auth = services.use("auth")
        if userid in gMainMenu:
            gMainMenu[userid].delete()
        gMainMenu[userid] = popuplib.easymenu("xamainmenu_"+str(userid), None, incoming_menu)
        gMainMenu[userid].settitle(gLanguage["eXtensible Admin"])
        for page in gMenusText:
            if gMenusPerm[page]:
                perm = gMenusPerm[page]
                auth = services.use("auth")
                if auth.isUseridAuthorized(userid, perm):
                    gMainMenu[userid].addoption(page, gMenusText[page], 1)
        gMainMenu[userid].send(userid)

###########################################
#EventScripts events and blocks start here#
###########################################

def load():
    global gMainMenu, gMainCommand
    es.dbgmsg(0, "[eXtensible Admin] Second loading part...")
    if not es.exists("command", "xa"):
        es.regcmd("xa", "xa/consolecmd", "eXtensible Admin")
    gMainCommand = Admin_command("xa", sendMenu, "xa_menu", "#admin")
    gMainCommand.register(["console","say"])
    es.dbgmsg(0, "[eXtensible Admin] Executing xa.cfg...")
    es.server.cmd('exec xa.cfg')
    #Mani compatibility
    es.dbgmsg(0, "[eXtensible Admin] Mani mode enabled = "+str(isManiMode()))
    if isManiMode():
        es.dbgmsg(0, "[eXtensible Admin] Executing mani_server.cfg...")
        manilib.loadVariables() #setup basic mani variables
        es.server.cmd("exec mani_server.cfg")
        manilib.loadModules() #load the mani modules if needed
    es.dbgmsg(0, "[eXtensible Admin] Executing xamodules.cfg...")
    es.server.cmd('exec xamodules.cfg')
    es.dbgmsg(0, "[eXtensible Admin] Updating xamodules.cfg...")
    setting.addVariables()
    es.dbgmsg(0, "[eXtensible Admin] Finished loading")

def unload():
    global gMainMenu, gMainCommand
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
    gMainCommand.unRegister(["console","say"])
    del gMainCommand
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
    elif subcmd == "permissions":
        permissions = []
        permissions.append(['Module', 'Permission', 'Level', 'Type', 'Name'])
        for module in sorted(gModules):
            x = gModules[module]
            for command in sorted(x.subCommands):
                permissions.append([str(x.name), str(x.subCommands[command].permission), str(x.subCommands[command].permissionlevel), 'command', str(x.subCommands[command].name)])
            for menu in x.subMenus:
                permissions.append([str(x.name), str(x.subMenus[menu].permission), str(x.subMenus[menu].permissionlevel), 'menu', str(x.subMenus[menu].name)])
        es.dbgmsg(0,"---------- List of permissions:")
        for perm in permissions:
            es.dbgmsg(0,("%-*s"%(15, perm[0]))+" "+("%-*s"%(20, perm[1]))+" "+("%-*s"%(8, "["+perm[2]+"]"))+" "+("%-*s"%(10, perm[3]))+" "+perm[4])
        es.dbgmsg(0,"----------")
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
                es.dbgmsg(0, "For more details, supply list level (0-2):")
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
                if not xcommand and argc >= 9:
                    if x:
                        command = str(es.getargv(4))
                        block = str(es.getargv(5))
                        perm = str(es.getargv(6))
                        permlvl = str(es.getargv(7))
                        target = bool(es.getargv(8))
                        x.addCommand(command, block, perm, permlvl, target)
                else:
                    es.dbgmsg(0,"Syntax: xa command create <module-name> <command-name> <block> <permission> <permission-level> <target 0/1>")
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
        es.dbgmsg(0,"Invalid xa subcommand, see http://www.eventscripts.com/pages/Xa/ for help")

#############################################
#EventScripts command/menu blocks start here#
#############################################

def incoming_server():
    command = es.getargv(0)
    if command in gCommandsPerm:
        block = gCommandsBlock[command]
        if callable(block):
            block()
        else:
            es.doblock(block)

def incoming_console():
    userid = es.getcmduserid()
    command = es.getargv(0)
    if command in gCommandsPerm:
        if gCommandsPerm[command]:
            perm = gCommandsPerm[command]
            auth = services.use("auth")
            if auth.isUseridAuthorized(userid, perm):
                block = gCommandsBlock[command]
                if callable(block):
                    block()
                else:
                    es.doblock(block)

def incoming_say():
    userid = es.getcmduserid()
    command = es.getargv(0)
    if command in gCommandsPerm:
        if gCommandsPerm[command]:
            perm = gCommandsPerm[command]
            auth = services.use("auth")
            if auth.isUseridAuthorized(userid, perm):
                block = gCommandsBlock[command]
                if callable(block):
                    block()
                else:
                    es.doblock(block)

def incoming_menu(userid, choice, name):
    if choice in gMenusPerm:
        if gMenusPerm[choice]:
            perm = gMenusPerm[choice]
            auth = services.use("auth")
            if auth.isUseridAuthorized(userid, perm):
                page = gMenusPage[choice]
                page.send(userid)
