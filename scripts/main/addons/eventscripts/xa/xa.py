#import EventScripts
import es
from es import server_var

#load and import the core
es.dbgmsg(0, "[eXtendable Admin] Begin loading...")
es.load("xa/core")
es.load("xa/module")
import core
from core.core import gModules
from core.core import gCommands
from core.core import gMenus
from core.core import gConfigs
from core.core import Admin_module
from core.core import Admin_command
from core.core import Admin_menu
from core.core import Admin_config

#import custom stuff
import popup
import playerlib
from popup import popup
from playerlib import playerlib

#plugin information
info = {}
info['name'] = "eXtendable Admin EventScripts Python addon"
info['version'] = "oy1"
info['author'] = "EventScripts Developers"
info['url'] = ""
info['description'] = ""
info['tags'] = ""

#Classes are stored in xa/core.py

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
        es.dbgmsg(0,"Xa.py: Cannot delete vote \""+pModuleid+"\", it does not exist")

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

###########################################
#EventScripts events and blocks start here#
###########################################

def load():
    if not es.exists("command", "xa"):
        es.regcmd("xa", "xa/consolecmd", "eXtendable Admin")
    es.dbgmsg(0, "[eXtendable Admin] Finished loading")

def unload():
    es.dbgmsg(0, "[eXtendable Admin] Begin unloading...")
    for module in gModules:
        es.dbgmsg(0, "[eXtendable Admin] Unloading module \""+module.name+"\"")
        es.unload("xa/module/"+module.name)
        del gModules[module]
    es.unload("xa/module")
    es.unload("xa/core")
    es.dbgmsg(0, "[eXtendable Admin] Finished unloading")

# TBD
#xa submenu create mymodule
#// ideally this is localizable/translated
#xa submenu set mymodule display "My Display Name"
#// precreated via popup
#xa submenu set mymodule popup mypopupid
#xa submenu set mymodule permission "permission-name" 

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
    else:
        es.dbgmsg(0,"Invalid xa subcommand, see http://www.eventscripts.com/pages/Xa/ for help")
        
##########################################
#EventScripts clientcmd blocks start here#
##########################################

# TBD

def incoming_server():
    print es.getargs()

def incoming_console():
    print es.getargs()

def incoming_say():
    print es.getargs()
