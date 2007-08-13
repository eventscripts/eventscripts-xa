import es
import xa
import os
from es import server_var
from os import getcwd

#global variables:
## gModules holds all the modules
gModules = {}
## gCommands holds all the commands
gCommands = {}
## gMenus holds all the menus
gMenus = {}
## gConfigs holds all the configs
gConfigs = {} 

es.dbgmsg(0, "[eXtendable Admin] Begin loading core...")

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
    def delete(self):
        xa.module_delete(self.name)
    def addrequirement(self, gModuleList):
        fails = []
        try:
            # try if gModuleList is just a single module
            module = str(gModuleList)
            modules = [module]
        except TypeError:
            modules = gModuleList
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
        try:
            # try if gModuleList is just a single module
            module = str(gModuleList)
            modules = [module]
        except TypeError:
            modules = gModuleList
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
    def __init__(self, gModule, gCommand, gBlock, gPerm, gPermLevel, gTarget=False):
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
            
# Admin_menu is the clientcmd class
class Admin_menu(object):
    def __init__(self, gModule, gMenu):
        #initialization of the module
        self.name = gMenu
        self.module = gModule
        # TODO:
        # - Add the menu management system
        #   * clientcmd like permissions for menus
        #   * needs to auto support player- and weaponlist menus with popup.easymenu
        #   * needs to have a main menu level with submenus
        #   * ...

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

def unload():
    es.dbgmsg(0, "[eXtendable Admin] Unloaded core")

es.dbgmsg(0, "[eXtendable Admin] Done loading core")
