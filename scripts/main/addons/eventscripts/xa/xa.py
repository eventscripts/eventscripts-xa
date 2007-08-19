import psyco
psyco.full()

#import EventScripts
import es
from es import server_var

#load and import the core
es.dbgmsg(0, "[eXtendable Admin] Begin loading...")
es.load("xa/module")

#import custom stuff
import os
import popup
import keymenu
import playerlib
from os import getcwd
from popup import popup
from keymenu import keymenu

#plugin information
info = es.AddonInfo()
info.name = "eXtendable Admin EventScripts Python addon"
info.version = "oy1"
info.author = "EventScripts Developers"
info.url = ""
info.description = ""

#global variables:
## gMainMenu holds XAs main menu
gMainMenu = None
## gModules holds all the modules
gModules = {}
## gCommands holds all the commands
gCommands = {}
## gMenus holds all the menus
gMenus = {}
## gConfigs holds all the configs
gConfigs = {}

#################### ######################################################
#Core Class Section# # PLEASE KEEP IN MIND THAT THOSE CLASSES ARE PRIVATE #
#################### ######################################################
# Admin_module is the module class
class Admin_module(object):
    def __init__(self, gModule):
        #initialization of the module
        self.name = gModule
        self.loaded = False
        self.requiredby = []
        self.requiredlist = []
        try:
            es.load("xa/module/"+self.name)
            es.dbgmsg(0, "[eXtendable Admin] Loaded module \""+self.name+"\"")
            self.loaded = True
        except:
            es.dbgmsg(0, "[eXtendable Admin] Failed loading module \""+self.name+"\"")
            self.loaded = False
    def load(self):
        if self.loaded == False:
            try:
                es.load("xa/module/"+self.name)
                es.dbgmsg(0, "[eXtendable Admin] Loaded module \""+self.name+"\"")
                self.loaded = True
            except:
                es.dbgmsg(0, "[eXtendable Admin] Failed loading module \""+self.name+"\"")
                self.loaded = False
                return False
            return True
        return False
    def unload(self):
        if self.loaded == True and len(self.requiredby) == 0:
            try:
                es.unload("xa/module/"+self.name)
                es.dbgmsg(0, "[eXtendable Admin] Unloaded module \""+self.name+"\"")
                self.loaded = False
                for module in self.requiredlist:
                    if module in gModules:
                        m = gModules[module]
                        m.requiredby.remove(self.name)
                        self.requiredlist.remove(m.name)
            except:
                es.dbgmsg(0, "[eXtendable Admin] Failed unloading module \""+self.name+"\"")
                self.loaded = True
                return False
            return True
        elif len(self.requiredby) > 0:
            es.dbgmsg(0, "[eXtendable Admin] Module \""+self.name+"\" is required by "+str(len(self.requiredby)))
            for module in self.requiredlist:
                if module in gModules:
                    es.dbgmsg(0, "[eXtendable Admin]  \""+module+"\"")
        return False
    def log(self, msg, speciallog = True):
        es.log(msg)
        if speciallog == True:
            # TODO
            # log to an XA log
            pass
    def delete(self):
        module_delete(self.name)
    def addrequirement(self, gModuleList):
        fails = []
        if type(gModuleList) == str:
            modules = [gModuleList]
        else:
            modules = list(gModuleList)
        for module in modules:
            if module in gModules:
                m = gModules[module]
                m.requiredby.append(self.name)
                self.requiredlist.append(m.name)
            else:
                fails.append(module)
        if len(fails) > 0:
            return fails
        else:
            return True
    def delrequirement(self, gModuleList):
        fails = []
        if type(gModuleList) == str:
            modules = [gModuleList]
        else:
            modules = list(gModuleList)
        for module in modules:
            if module in self.requiredlist:
                m = gModules[module]
                m.requiredby.remove(self.name)
                self.requiredlist.remove(m.name)
            else:
                fails.append(module)
        if len(fails) > 0:
            return fails
        else:
            return True
    def information(self, listlevel):
        if listlevel >= 1:
            es.dbgmsg(0, " ")
        es.dbgmsg(0, self.name)
        if listlevel >= 1:
            es.dbgmsg(0, "  Loaded:       "+str(self.loaded))
        if listlevel >= 2:
            es.dbgmsg(0, "  Required by:  "+str(len(self.requiredby)))
            for module in self.requiredby:
                es.dbgmsg(0,"    "+module)
            es.dbgmsg(0, "  Requires:     "+str(len(self.requiredlist)))
            for module in self.requiredlist:
                es.dbgmsg(0,"    "+module)

# Admin_command is the clientcmd class
class Admin_command(object):
    def __init__(self, gCommand, gModule, gBlock, gPerm, gPermLevel, gTarget=False):
        #initialization of the module
        self.name = gCommand
        self.module = gModule
        self.block = gBlock
        self.permission = gPerm
        self.permissionlevel = gPermLevel
        self.target = gTarget
        self.server = False
        self.console = False
        self.say = False
    def create(self, gList):
        cmdlist = list(gList)
        if "server" in cmdlist and self.server == False:
            es.regcmd(self.name, "xa/incoming_server", "eXtendable Admin command")
            self.server = True
        if "console" in cmdlist and self.console == False:
            es.server.cmd("clientcmd create console "+str(self.name)+" xa/incoming_console "+str(self.permission)+" "+str(self.permissionlevel))
            self.console = True
        if "say" in cmdlist and self.say == False:
            es.server.cmd("clientcmd create say "+str(self.name)+" xa/incoming_say "+str(self.permission)+" "+str(self.permissionlevel))
            self.say = True
    def delete(self, gList):
        cmdlist = list(gList)
        if "console" in cmdlist and self.console == True:
            es.server.cmd("clientcmd delete console "+str(self.name))
            self.console = False
        if "say" in cmdlist and self.say == True:
            es.server.cmd("clientcmd delete say "+str(self.name))
            self.say = False
    def information(self, listlevel):
        if listlevel >= 1:
            es.dbgmsg(0, " ")
        es.dbgmsg(0, self.name)
        if listlevel >= 1:
            es.dbgmsg(0, "  Module:       "+str(self.module))
            es.dbgmsg(0, "  Block:        "+str(self.block))
            es.dbgmsg(0, "  Server cmd:   "+str(self.server))
            es.dbgmsg(0, "  Console cmd:  "+str(self.console))
            es.dbgmsg(0, "  Say cmd:      "+str(self.say))
            es.dbgmsg(0, "  Target:       "+str(self.target))
            es.dbgmsg(0, "  Permission:   "+str(self.permission))
            es.dbgmsg(0, "  Perm-level:   "+str(self.permissionlevel))
            
# Admin_menu is the clientcmd class
class Admin_menu(object):
    def __init__(self, gMenu, gModule, gDisplay, gMenuName, gPerm, gPermLevel):
        #initialization of the module
        self.name = gMenu
        self.module = gModule
        self.display = gDisplay
        self.menu = gMenuName
        self.menutype = ""
        self.menuobj = None
        self.permission = gPerm
        self.permissionlevel = gPermLevel
        if popup.exists(self.menu):
            self.menutype = "popup"
            self.menuobj = popup.find(self.menu)
        elif keymenu.exists(self.menu):
            self.menutype = "keymenu"
            self.menuobj = keymenu.find(self.menu)
        gMainMenu.addoption(self.name, self.display, 1)
    def delete(self):
        menu_delete(self.name)
    def setdisplay(self, display):
        self.display = display
        gMainMenu.setoption(self.name, self.display, 1)
        return True
    def setmenu(self, menu):
        if popup.exists(menu):
            self.menu = menu
            self.menutype = "popup"
            self.menuobj = popup.find(self.menu)
            return True
        elif keymenu.exists(menu):
            self.menu = menu
            self.menutype = "keymenu"
            self.menuobj = keymenu.find(self.menu)
            return True
        return False
    def setpermission(self, perm, permlevel):
        self.permission = perm
        self.permissionlevel = permlevel
    def information(self, listlevel):
        if listlevel >= 1:
            es.dbgmsg(0, " ")
        es.dbgmsg(0, self.name)
        if listlevel >= 1:
            es.dbgmsg(0, "  Module:       "+str(self.module))
            es.dbgmsg(0, "  Display:      "+str(self.display))
            es.dbgmsg(0, "  Menuname:     "+str(self.menu))
            es.dbgmsg(0, "  Menutype:     "+str(self.menutype))
            es.dbgmsg(0, "  Permission:   "+str(self.permission))
            es.dbgmsg(0, "  Perm-level:   "+str(self.permissionlevel))

# Admin_config is the config class for modules
class Admin_config(object):
    def __init__(self):
        self.name = "null for now"
    def loadfile(self, filepath):
        try:
            fp = open(filepath)
        except IOError:
            return False
        else:
            return fp
    def loadDefaultConfig(self, filename):
        self.dfilename = filename
    def loadCustomConfig(self, filename):
        self.cfilename = filename
    def loadManiConfig(self, filename, filter=0):
        # Lets see what files we are loadign and how to parse them
        if filename == "mani_server.cfg":
            manicfg = self.loadfile(getcwd() + "/cstrike/cfg/mani_server.cfg")
            if manicfg:
                return self.parse_mani_server(manicfg, filter)
                
    def parse_mani_server(self, fp, filter):
        manivars = {}
        for line in fp:
            line = line.strip("\n")
            line = line.strip("\r")
            if filter:
                if line.startswith(filter):
                    temp = line.split(" ")
                    vname = temp[0]
                    temp.pop(0)
                    vstring = ""
                    for sect in temp:
                        vstring = vstring + " " + sect
                    vstring = vstring.strip(" ")
                    vstring = vstring.strip("\"")
                    manivars[vname] = vstring
            else:
            # return all vars then!
                if line.startswith("mani_"):
                    temp = line.split(" ")
                    vname = temp[0]
                    temp.pop(0)
                    vstring = ""
                    for sect in temp:
                        vstring = vstring + " " + sect
                    vstring = vstring.strip(" ")
                    vstring = vstring.strip("\"")
                    manivars[vname] = vstring
        return manivars

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
def module_create(pModuleid):
    #create new module
    gModules[pModuleid] = Admin_module(pModuleid)
    return gModules[pModuleid]

def module_delete(pModuleid):
    #delete a module
    if (pModuleid in gModules):
        if bool(gModules[pModuleid].loaded):
            gModules[pModuleid].unload()
        del gModules[pModuleid]
    else:
        es.dbgmsg(0,"Xa.py: Cannot delete module \""+pModuleid+"\", it does not exist")

def module_exists(pModuleid):
    #does named module exist
    return (pModuleid in gModules)

def module_isloaded(pModuleid):
    #does named module exist and is loaded
    if (pModuleid in gModules):
        return gModules[pModuleid].loaded
    return False

def module_isrequired(pModuleid):
    #does named module exist and is required
    if (pModuleid in gModules):
        return bool(len(gModules[pModuleid].requiredby))
    return False

def module_find(pModuleid):
    #return class instance of named module
    if (pModuleid in gModules):
        return gModules[pModuleid]
    return None

def module_addrequirement(pModuleid, modules):
    #add a required module for the module
    if (pModuleid in gModules):
        return gModules[pModuleid].addrequirement(modules)
    return None

def module_delrequirement(pModuleid, modules):
    #delete a required module for the module
    if (pModuleid in gModules):
        return gModules[pModuleid].delrequirement(modules)
    return None
    
#########################
#Menu methods start here#
#########################
def menu_create(pMenuid, module, display, menuname, perm, permlvl):
    #create new menu
    gMenus[pMenuid] = Admin_menu(pMenuid, module, display, menuname, perm, permlvl)
    return gMenus[pMenuid]

def menu_delete(pMenuid):
    #delete a menu
    if (pMenuid in gMenus):
        gMainMenu.setoption(gMenus[pMenuid].name, gMenus[pMenuid].display, 0)
        del gMenus[pMenuid]
    else:
        es.dbgmsg(0,"Xa.py: Cannot delete menu \""+pMenuid+"\", it does not exist")

def menu_exists(pMenuid):
    #does named menu exist
    return (pMenuid in gMenus)

def menu_find(pMenuid):
    #return class instance of named menu
    if (pMenuid in gMenus):
        return gMenus[pMenuid]
    return None

def menu_setdisplay(pMenuid, display):
    #set the display text for a menu
    if (pMenuid in gMenus):
        return gMenus[pMenuid].setdisplay(display)
    return None

def menu_setmenu(pMenuid, menu):
    #set the menu for the module
    if (pMenuid in gMenus):
        return gMenus[pMenuid].setmenu(menu)
    return None

def menu_setpermission(pMenuid, perm, permlevel):
    #set the permission for the menu
    if (pMenuid in gMenus):
        return gMenus[pMenuid].setpermission(perm, permlevel)
    return None

###########################################
#EventScripts events and blocks start here#
###########################################

def load():
    global gMainMenu
    if not es.exists("command", "xa"):
        es.regcmd("xa", "xa/consolecmd", "eXtendable Admin")
    gMainMenu = popup.easymenu("_xa_mainmenu", "_xa_choice", incoming_menu)
    gMainMenu.c_titleformat = "eXtendable Admin" + (" "*(30-len("eXtendable Admin"))) + " (%p/%t)"
    es.dbgmsg(0, "[eXtendable Admin] Finished loading")

def unload():
    global gMainMenu
    es.dbgmsg(0, "[eXtendable Admin] Begin unloading...")
    for module in gModules:
        es.dbgmsg(0, "[eXtendable Admin] Unloading module \""+module.name+"\"")
        es.unload("xa/module/"+module.name)
        del gModules[module]
    if popup.exists("_xa_mainmenu"):
        if gMainMenu:
            gMainMenu.delete()
        else:
            gMainMenu = popup.find("_xa_mainmenu")
            gMainMenu.delete()
        gMainMenu = None
    es.unload("xa/module")
    es.dbgmsg(0, "[eXtendable Admin] Finished unloading")

def consolecmd():
    #Command from server console or non-python script
    subcmd = es.getargv(1).lower()
    seccmd = es.getargv(2).lower()
    xname = es.getargv(3)
    argc = es.getargc()
    if subcmd == "module":
        if xname in gModules:
            x = gModules[xname]
        else:
            x = None
        if seccmd == "load":
            if xname:
                if x:
                    if not x.load():
                        es.dbgmsg(0,"[eXtendable Admin] Could not load module \""+xname+"\", it might already be loaded")
                else:
                    module_create(xname)
            else:
                es.dbgmsg(0,"Syntax: xa module load <module-name>")
        elif seccmd == "unload":
            if xname:
                if x:
                    if not x.unload():
                        es.dbgmsg(0,"[eXtendable Admin] Could not unload module \""+xname+"\", it might be required")
                    else:
                        module_delete(xname)
                else:
                    es.dbgmsg(0,"[eXtendable Admin] Could not unload module \""+xname+"\", it is not loaded")
            else:
                es.dbgmsg(0,"Syntax: xa module load <module-name>")
        elif seccmd == "exists":
            if argc == 4:
                xname = es.getargv(3)
                retvar = es.getargv(4)
                es.set(retvar,int(module_exists(xname)))
            else:
                es.dbgmsg(0,"Syntax: xa module exists <module-name> <var>")
        elif seccmd == "isloaded":
            if argc == 4:
                xname = es.getargv(3)
                retvar = es.getargv(4)
                es.set(retvar,int(module_isloaded(xname)))
            else:
                es.dbgmsg(0,"Syntax: xa module isloaded <module-name> <var>")
        elif seccmd == "isrequired":
            if argc == 4:
                xname = es.getargv(3)
                retvar = es.getargv(4)
                es.set(retvar,int(module_isrequired(xname)))
            else:
                es.dbgmsg(0,"Syntax: xa module isrequired <module-name> <var>")
        elif seccmd == "addrequirement":
            if xname:
                if x:
                    result = x.addrequirement(es.getargv(4))
                    if result == True:
                        es.dbgmsg(0,"[eXtendable Admin] Added module \""+es.getargv(4)+"\" as a requirement for module \""+xname+"\"")
                    else:
                        for failed in result:
                            es.dbgmsg(0,"Xa.py: Could not add module \""+failed+"\" as a requirement for module \""+xname+"\"")
                else:
                    es.dbgmsg(0,"Xa.py: The module \""+xname+"\" does not exists")
            else:
                es.dbgmsg(0,"Syntax: xa module addrequirement <module-name> <required-module>")
        elif seccmd == "delrequirement":
            if xname:
                if x:
                    result = x.delrequirement(es.getargv(4))
                    if result == True:
                        es.dbgmsg(0,"[eXtendable Admin] Deleted module \""+es.getargv(4)+"\" as a requirement from module \""+xname+"\"")
                    else:
                        for failed in result:
                            es.dbgmsg(0,"Xa.py: Could not delete module \""+failed+"\" as a requirement from module \""+xname+"\"")
                else:
                    es.dbgmsg(0,"Xa.py: The module \""+xname+"\" does not exists")
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
    if subcmd == "menu":
        if xname in gMenus:
            x = gMenus[xname]
        else:
            x = None
        if seccmd == "create":
            if xname and argc == 9:
                if not x:
                    module = str(es.getargv(4))
                    display = str(es.getargv(5))
                    menuname = str(es.getargv(6))
                    perm = str(es.getargv(7))
                    permlvl = str(es.getargv(8))
                    menu_create(xname, module, display, menuname, perm, permlvl)
            else:
                es.dbgmsg(0,"Syntax: xa menu create <menu-name> <module-name> <display-name> <popup/keymenu-name> <permission> <permission-level>")
        elif seccmd == "delete":
            if xname:
                if x:
                    module_delete(xname)
                else:
                    es.dbgmsg(0,"[eXtendable Admin] Could not delete the menu \""+xname+"\", it does not exists")
            else:
                es.dbgmsg(0,"Syntax: xa menu delete <menu-name>")
        elif seccmd == "exists":
            if argc == 4:
                xname = es.getargv(3)
                retvar = es.getargv(4)
                es.set(retvar,int(module_exists(xname)))
            else:
                es.dbgmsg(0,"Syntax: xa module exists <module-name> <var>")
        elif seccmd == "setdisplay":
            if xname:
                if x:
                    display = str(es.getargv(4))
                    x.setdisplay(display)
                else:
                    es.dbgmsg(0,"Xa.py: The menu \""+xname+"\" does not exists")
            else:
                es.dbgmsg(0,"Syntax: xa menu setdisplay <menu-name> <display-name>")
        elif seccmd == "setmenu":
            if xname:
                if x:
                    menuname = str(es.getargv(4))
                    if popup.exists(menuname) or keymenu.exists(menuname):
                        x.setmenu(menuname)
                    else:
                        es.dbgmsg(0,"Xa.py: There is no popup or keymenu named \""+menuname+"\"")
                else:
                    es.dbgmsg(0,"Xa.py: The menu \""+xname+"\" does not exists")
            else:
                es.dbgmsg(0,"Syntax: xa menu setmenu <menu-name> <popup/keymenu-name>")
        elif seccmd == "setpermission":
            if xname:
                if x:
                    perm = str(es.getargv(4))
                    permlvl = str(es.getargv(5))
                    x.setpermission(perm, permlvl)
                else:
                    es.dbgmsg(0,"Xa.py: The menu \""+xname+"\" does not exists")
            else:
                es.dbgmsg(0,"Syntax: xa menu setdisplay <menu-name> <display-name>")
        elif seccmd == "list":
            es.dbgmsg(0,"---------- List of menus:")
            if argc == 3:
                listlevel = 0
            else:
                listlevel = int(xname)
            for menu in gMenus:
                x = gMenus[menu]
                x.information(listlevel)
            if argc == 3:
                es.dbgmsg(0, " ")
                es.dbgmsg(0, "For more details, supply list level (0-1):")
                es.dbgmsg(0, "Syntax: xa menu list [level]")
            es.dbgmsg(0,"----------")
        elif seccmd == "info":
            if argc >= 4:
                if x:
                    x.information(1)
            else:
                es.dbgmsg(0, "Syntax: xa menu info <menu-name>")
        else:
            es.dbgmsg(0,"Syntax: xa menu <subcommand>")
    else:
        es.dbgmsg(0,"Invalid xa subcommand, see http://www.eventscripts.com/pages/Xa/ for help")
        
##########################################
#EventScripts clientcmd blocks start here#
##########################################

# TBD

def incoming_menu(userid, choice, name):
    print userid, choice, name

def incoming_server():
    print es.getargs()

def incoming_console():
    print es.getargs()

def incoming_say():
    print es.getargs()