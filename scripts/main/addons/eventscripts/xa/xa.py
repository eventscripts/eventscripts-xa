# ==============================================================================
#   IMPORTS
# ==============================================================================
# Python Imports
import os
import shutil
import hotshot.stats

# EventScripts Imports
import es
import services
import gamethread
import playerlib
import popuplib
import keymenulib
import settinglib
import keyvalues
import cmdlib
import cfglib

# ==============================================================================
#   ADDON REGISTRATION
# ==============================================================================
# Version info
__version__ = '1.0.0.415'
es.ServerVar('eventscripts_xa', __version__, 'eXtensible Admin').makepublic()
es.dbgmsg(0, '[eXtensible Admin] Version: %s' % __version__)
es.dbgmsg(0, '[eXtensible Admin] Begin loading...')

# Register with EventScripts
info = es.AddonInfo()
info.name       = 'eXtensible Admin'
info.version    = __version__
info.url        = 'http://forums.mattie.info/cs/forums/viewforum.php?f=97'
info.basename   = 'xa'
info.author     = 'EventScripts Developers'

# ==============================================================================
#   LOAD XA LIBRARIES
# ==============================================================================
import configparser
reload(configparser)
import language
reload(language)
import logging
reload(logging)
import playerdata
reload(playerdata)
import setting
reload(setting)

# ==============================================================================
#   GLOBALS
# ==============================================================================
# Imported libraries
gImportLibraries = dir()

# Core variables
gCoreVariables = {}
gCoreVariables['log']           = es.ServerVar('xa_log',            0,      'Activates the module logging')
gCoreVariables['debug']         = es.ServerVar('xa_debug',          0,      'Activates the module/library debugging')
gCoreVariables['debugprofile']  = es.ServerVar('xa_debugprofile',   0,      'Activates the module/library profiling')
gCoreVariables['manimode']      = es.ServerVar('xa_manimode',       0,      'Is Mani compatibility mode active?')
gCoreVariables['sayprefix']     = es.ServerVar('xa_sayprefix',      '!',    'Say command prefix')

# Main menu and command instance
gMainConfig = None
gMainMenu = {}
gMainCommand = None

# Module dict
gModules = {}
gModulesLoading = False

# ==============================================================================
#   HELPER CLASSES
# ==============================================================================
class Admin_libfunc(object):
    def __init__(self, gLib, gFunc, gModule):
        self._xalib = gLib
        self._xalibfunc = gFunc
        self._xalibfunccalls = 0
        self._xalibfuncstats = {'calls':0, 'times':0}
        self._xamod = gModule
        
    def __call__(self, *args, **kw):
        self._xalibfunccalls += 1
        if int(gCoreVariables['debug']) >= 1 or int(gCoreVariables['debugprofile']) > 0: #check debug here to be faster
            fn = '%s/xa.prof' % coredir()
            pr = hotshot.Profile(fn)
            re = pr.runcall(self._xalibfunc, *(self._xamod,)+args, **kw)
            pr.close()
            st = hotshot.stats.load(fn)
            st.strip_dirs()
            st.sort_stats('time', 'calls')
            if int(gCoreVariables['debug']) >= 2:
                es.dbgmsg(0, '--------------------')
                es.dbgmsg(0, ('Admin_libfunc %d: __call__(%s.%s [%s], %s, %s)' % (self._xalibfunccalls, str(self._xalib.__name__), str(self._xalibfunc.__name__), str(self._xamod), args, kw)))
                es.dbgmsg(0, ('Admin_libfunc %d: Profile Statistics' % (self._xalibfunccalls)))
                st.print_stats(20)
                es.dbgmsg(0, '--------------------')
            elif int(gCoreVariables['debug']) == 1:
                es.dbgmsg(0, ('Admin_libfunc %d: __call__(%s.%s [%s], %s, %s)' % (self._xalibfunccalls, str(self._xalib.__name__), str(self._xalibfunc.__name__), str(self._xamod), args, kw)))
                es.dbgmsg(0, ('Admin_libfunc %d: %d calls in %f CPU seconds' % (self._xalibfunccalls, st.total_calls, st.total_tt)))
            if int(gCoreVariables['debugprofile']) > 0:
                self._xalibfuncstats['calls'] += st.total_calls
                self._xalibfuncstats['times'] += st.total_tt
            if os.path.exists(fn):
                os.unlink(fn)
            return re
        else:
            return self._xalibfunc(self._xamod, *args, **kw)

class Admin_lib(object):
    def __init__(self, gLib, gModule):
        self._xalib = gLib
        self._xalibcalls = 0
        self._xalibfuncs = {}
        self._xamod = gModule
        
    def __getattr__(self, name):
        self._xalibcalls += 1
        if int(gCoreVariables['debug']) >= 2: #check debug here to be faster
            es.dbgmsg(0, ('Admin_lib %d: __getattr__(%s [%s], %s)' % (self._xalibcalls, str(self._xalib.__name__), str(self._xamod), name)))
        if self._xalib.__dict__.has_key(name) and not name.startswith('_'):
            if not name in self._xalibfuncs:
                self._xalibfuncs[name] = Admin_libfunc(self._xalib, self._xalib.__dict__[name], self._xamod)
            return self._xalibfuncs[name]
        else:
            raise AttributeError, name

# ==============================================================================
#   CORE CLASSES
# ==============================================================================
class Admin_module(object):
    def __init__(self, gModule):
        self._xa = None
        self._xamod = None
        self._xalibs = {}
        self.name = gModule
        self.subCommands = {}
        self.subMenus = {}
        self.customPermissions = {}
        self.requiredFrom = []
        self.requiredList = []
        self.required = 0
        self.variables = {}
        self.getCore()
        
    def __str__(self):
        return self.name
        
    def __getattr__(self, name):
        self.getModule()
        if (name in gImportLibraries) and (self._xa.__dict__.has_key(name)):
            if not name in self._xalibs:
                self._xalibs[name] = Admin_lib(self._xa.__dict__[name], self)
            return self._xalibs[name]
        elif (name in gModules) and (name in self.requiredList):
            for mod in es.addons.getAddonList():
                if mod.__name__ == 'xa.modules.%s.%s'%(name, name):
                    if not name in self._xalibs:
                        self._xalibs[name] = Admin_lib(mod, self)
                    return self._xalibs[name]
            raise AttributeError, name
        elif (self._xamod.__dict__.has_key(name)):
            return Admin_lib(self._xamod, self).__getattr__(name)
        else:
            raise AttributeError, name
            
    def getAddonInfo(self):
        self.getModule()
        for item in self._xamod.__dict__:
            if isinstance(self._xamod.__dict__[item], es.AddonInfo):
                return self._xamod.__dict__[item]
                
    def getCore(self):
        if not self._xa:
            for mod in es.addons.getAddonList():
                if mod.__name__ == 'xa.xa':
                    self._xa = mod
        return self._xa
        
    def getModule(self):
        if not self._xamod:
            for mod in es.addons.getAddonList():
                if mod.__name__ == 'xa.modules.%s.%s'%(self.name, self.name):
                    self._xamod = mod
        return self._xamod
        
    def delete(self):
        unregister(self.name)
        
    def unregister(self):
        unregister(self.name)
        
    def unload(self):
        xa_unload(self.name)
        
    def addRequirement(self, gModuleList):
        if isinstance(gModuleList, str):
            addlist = [gModuleList]
        else:
            addlist = list(gModuleList)
        for module in addlist:
            if module in modules():
                module = find(module)
                module.required += 1
                module.requiredFrom.append(self.name)
                self.requiredList.append(module.name)
                
    def delRequirement(self, gModuleList):
        if isinstance(gModuleList, str):
            dellist = [gModuleList]
        else:
            dellist = list(gModuleList)
        for module in dellist:
            if exists(module) and (module in self.requiredList):
                module = find(module)
                module.required -= 1
                module.requiredFrom.remove(self.name)
                self.requiredList.remove(module.name)
                
    def addCommand(self, command, block, perm=None, permlvl=None, descr='eXtensible Admin command', mani=False):
        self.subCommands[command] = Admin_command(command, block, perm, permlvl, descr, mani)
        return self.subCommands[command]
        
    def delCommand(self, command):
        if (command in self.subCommands):
            if self.subCommands[command]:
                self.subCommands[command].unregister(['server','console','say'])
                self.subCommands[command] = None
                
    def isCommand(self, command):
        if (command in self.subCommands):
            return True
        return False
        
    def findCommand(self, command):
        if (command in self.subCommands):
            return self.subCommands[command]
            
    def addMenu(self, menu, display, menuname, perm=None, permlvl=None):
        self.subMenus[menu] = Admin_menu(menu, display, menuname, perm, permlvl)
        return self.subMenus[menu]
        
    def delMenu(self, menu):
        if (menu in self.subMenus):
            if self.subMenus[menu]:
                self.subMenus[menu].unregister()
                self.subMenus[menu] = None
                
    def isMenu(self, menu):
        if (menu in self.subMenus):
            return True
        return False
        
    def findMenu(self, menu):
        if (menu in self.subMenus):
            return self.subMenus[menu]
            
    def registerCapability(self, auth_capability, auth_recommendedlevel, auth_type='ADMIN'):
        self.customPermissions[auth_capability] = {'level':str(auth_recommendedlevel).upper(), 'type':str(auth_type).upper()}
        return registerCapability(auth_capability, getLevel(auth_recommendedlevel))
        
    def isUseridAuthorized(self, auth_userid, auth_capability):
        return isUseridAuthorized(auth_userid, auth_capability)
        
    def information(self, listlevel):
        if listlevel >= 1:
            es.dbgmsg(0, ' ')
        es.dbgmsg(0, self.name)
        if listlevel >= 1:
            es.dbgmsg(0, '  Required by:  '+str(len(self.requiredFrom)))
            for module in self.requiredFrom:
                es.dbgmsg(0,'    '+module)
            es.dbgmsg(0, '  Requires:     '+str(len(self.requiredList)))
            for module in self.requiredList:
                es.dbgmsg(0,'    '+module)
            es.dbgmsg(0, '  ')
            es.dbgmsg(0, '  Variables:    '+str(len(self.variables)))
            for var in self.variables:
                es.dbgmsg(0,'    '+var)
        if listlevel >= 2:
            es.dbgmsg(0, '  ')
            es.dbgmsg(0, '  Libs & Funcs: '+str(len(self._xalibs)))
            for lib in self._xalibs:
                es.dbgmsg(0,'    '+lib+' ['+str(self._xalibs[lib]._xalibcalls)+' calls]')
                for func in self._xalibs[lib]._xalibfuncs:
                    if self._xalibs[lib]._xalibfuncs[func]._xalibfuncstats['calls'] > 0:
                        es.dbgmsg(0,'        '+func+' ['+str(self._xalibs[lib]._xalibfuncs[func]._xalibfunccalls)+' calls, '+str(self._xalibs[lib]._xalibfuncs[func]._xalibfuncstats['calls'])+' subcalls, '+str(self._xalibs[lib]._xalibfuncs[func]._xalibfuncstats['times'])+' CPU seconds]')
                    else:
                        es.dbgmsg(0,'        '+func+' ['+str(self._xalibs[lib]._xalibfuncs[func]._xalibfunccalls)+' calls]')
            es.dbgmsg(0, '  -------------')

class Admin_command(object):
    def __init__(self, gCommand, gBlock, gPerm=None, gPermLevel=None, gDescription='eXtensible Admin command', gManiComp=False):
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
        
    def __str__(self):
        return self.name
        
    def register(self, gList):
        if isinstance(gList, str):
            cmdlist = [gList]
        else:
            cmdlist = list(gList)
        if 'server' in cmdlist and not self.server:
            if self.manicomp and isManiMode() and self.name.startswith('xa_'):
                cmdlib.registerServerCommand('ma_'+self.name[3:], self.incomingServer, self.descr)
            cmdlib.registerServerCommand(self.name, self.incomingServer, self.descr)
            self.server = True
        if 'console' in cmdlist and not self.console:
            if self.manicomp and isManiMode() and self.name.startswith('xa_'):
                cmdlib.registerClientCommand('ma_'+self.name[3:], self.incomingConsole, self.descr, self.permission, self.permissionlevel)
            cmdlib.registerClientCommand(self.name, self.incomingConsole, self.descr, self.permission, self.permissionlevel)
            self.console = True
        if 'say' in cmdlist and not self.say:
            if self.name.startswith('xa_'):
                cmdlib.registerSayCommand(str(gCoreVariables['sayprefix'])+self.name[3:], self.incomingSay, self.descr, self.permission, self.permissionlevel)
            cmdlib.registerSayCommand(self.name, self.incomingSay, self.descr, self.permission, self.permissionlevel)
            self.say = True
        if 'chat' in cmdlist and not self.chat:
            if not self.incomingChat in es.addons.SayListeners:
                es.addons.registerSayFilter(self.incomingChat)
            self.chat = True
            
    def unregister(self, gList):
        if isinstance(gList, str):
            cmdlist = [gList]
        else:
            cmdlist = list(gList)
        if 'server' in cmdlist and self.server:
            if self.name.startswith('xa_'):
                cmdlib.unregisterServerCommand('ma_'+self.name[3:])
            cmdlib.unregisterServerCommand(self.name)
            self.server = False
        if 'console' in cmdlist and self.console:
            if self.name.startswith('xa_'):
                cmdlib.unregisterClientCommand('ma_'+self.name[3:])
            cmdlib.unregisterClientCommand(self.name)
            self.console = False
        if 'say' in cmdlist and self.say:
            if self.name.startswith('xa_'):
                cmdlib.unregisterSayCommand(str(gCoreVariables['sayprefix'])+self.name[3:])
            cmdlib.unregisterSayCommand(self.name)
            self.say = False
        if 'chat' in cmdlist and self.chat:
            if self.incomingChat in es.addons.SayListeners:
                es.addons.unregisterSayFilter(self.incomingChat)
            self.chat = False
            
    def callBlock(self, userid, args):
        try:
            self.block(userid, args)
        except TypeError:
            try:
                self.block()
            except TypeError:
                es.doblock(self.block)
                
    def incomingServer(self, args):
        if self.server:
            self.callBlock(0, args)
            
    def incomingConsole(self, userid, args):
        if self.console:
            self.callBlock(userid, args)
            
    def incomingSay(self, userid, args):
        if self.say:
            self.callBlock(userid, args)
            
    def incomingChat(self, userid, message, teamonly):
        if self.chat:
            output = message
            if output[0] == output[-1:] == '"':
                output = output[1:-1]
            command = output.split(' ')[0]
            if command.startswith('ma_'):
                command = 'xa_'+command[3:]
            elif command.startswith(str(gCoreVariables['sayprefix'])):
                command = 'xa_'+command[len(str(gCoreVariables['sayprefix'])):]
            if command == self.name and not self.permission or isUseridAuthorized(userid, self.permission):
                self.callBlock(userid, cmdlib.cmd_manager.CMDArgs(output.split(' ')[1:] if len(output.split(' ')) > 1 else []))
        return (userid, message, teamonly)
        
    def information(self, listlevel):
        if listlevel >= 1:
            es.dbgmsg(0, ' ')
        es.dbgmsg(0, self.name)
        if listlevel >= 1:
            es.dbgmsg(0, '  Block:        '+str(self.block))
            es.dbgmsg(0, '  Server cmd:   '+str(self.server))
            es.dbgmsg(0, '  Console cmd:  '+str(self.console))
            es.dbgmsg(0, '  Say cmd:      '+str(self.say))
            es.dbgmsg(0, '  Chat cmd:     '+str(self.chat))
            es.dbgmsg(0, '  Mani cmd:     '+str(self.manicomp))
            es.dbgmsg(0, '  Capability:   '+str(self.permission))
            es.dbgmsg(0, '  Level:        '+str(self.permissionlevel))
            es.dbgmsg(0, '  Description:  '+str(self.descr))

class Admin_menu(object):
    def __init__(self, gMenu, gDisplay, gMenuName, gPerm=None, gPermLevel=None):
        self.name = gMenu
        self.display = gDisplay
        self.menu = gMenuName
        self.menutype = ''
        self.menuobj = None
        self.permission = gPerm
        self.permissionlevel = gPermLevel
        if popuplib.exists(self.menu):
            self.menutype = 'popup'
            self.menuobj = popuplib.find(self.menu)
        elif keymenulib.exists(self.menu):
            self.menutype = 'keymenu'
            self.menuobj = keymenulib.find(self.menu)
        elif settinglib.exists(self.menu):
            self.menutype = 'setting'
            self.menuobj = settinglib.find(self.menu)
        if self.permission and self.permissionlevel:
            registerCapability(self.permission, getLevel(self.permissionlevel))
        self.addBackButton()
        
    def __str__(self):
        return self.name
        
    def unregister(self):
        self.menuobj = None
        
    def setDisplay(self, display):
        self.display = display
        
    def setMenu(self, menu):
        if popuplib.exists(menu):
            self.menu = menu
            self.menutype = 'popup'
            self.menuobj = popuplib.find(self.menu)
        elif keymenulib.exists(menu):
            self.menu = menu
            self.menutype = 'keymenu'
            self.menuobj = keymenulib.find(self.menu)
        elif settinglib.exists(menu):
            self.menu = menu
            self.menutype = 'setting'
            self.menuobj = settinglib.find(self.menu)
        else:
            return False
        return self.addBackButton()
        
    def addBackButton(self):
        if isinstance(self.menuobj, popuplib.Popup_easymenu):
            self.menuobj.menuselect = sendMenu
            self.menuobj.c_exitformat = '0. Back'
        elif isinstance(self.menuobj, keymenulib.Keymenu_keymenu):
            try:
                self.menuobj.popup.menuselect = sendMenu
                self.menuobj.popup.c_exitformat = '0. Back'
            except:
                return False ## keymenulib was probably changed, don't worry, no back button then
        return True
        
    def information(self, listlevel):
        if listlevel >= 1:
            es.dbgmsg(0, ' ')
        es.dbgmsg(0, self.name)
        if listlevel >= 1:
            es.dbgmsg(0, '  Display:      '+str(self.display))
            es.dbgmsg(0, '  Menuname:     '+str(self.menu))
            es.dbgmsg(0, '  Menutype:     '+str(self.menutype))
            es.dbgmsg(0, '  Capability:   '+str(self.permission))
            es.dbgmsg(0, '  Level:        '+str(self.permissionlevel))

class Admin_mani(object):
    def __init__(self):
        self.admincmd = Admin_command('admin', sendMenu)
        self.admincmd.register(['console'])
        self.config = configparser.getList(self, 'addons/eventscripts/xa/static/maniconfig.txt', True)
        self.permissions = configparser.getKeyList(self, 'addons/eventscripts/xa/static/manipermission.txt', True)

    def loadVariables(self):
        if self.config:
            for line in self.config:
                linelist = map(str, line.strip().split('|', 2))
                es.ServerVar(linelist[0], linelist[1], linelist[2])
        else:
            raise IOError, 'Could not find xa/static/maniconfig.txt!'

    def hookAuthProvider(self):
        if self.permissions:
            auth = services.use('auth')
            if auth.name in ('group_auth', 'basic_auth', 'mani_basic_auth', 'ini_tree_auth'):
                es.dbgmsg(0, '[eXtensible Admin] We will be converting capabilities to Mani flags')
                self.isIdAuthorized = auth.isIdAuthorized
                auth.isIdAuthorized = self.hookIsIdAuthorized
                es.dbgmsg(0, '[eXtensible Admin] Finished Mani setup for Mani flags based Auth')
        else:
            raise IOError, 'Could not find xa/static/manipermission.txt!'

    def hookIsIdAuthorized(self, auth_identifier, auth_capability):
        if self.permissions:
            if auth_capability in self.permissions['adminflags']:
                return self.isIdAuthorized(auth_identifier, auth_capability) or self.isIdAuthorized(auth_identifier, 'mani_flag_%s'%self.permissions['adminflags'][auth_capability])
            else:
                return self.isIdAuthorized(auth_identifier, auth_capability)
        else:
            raise IOError, 'Could not find xa/static/manipermission.txt!'

# ==============================================================================
#   MODULE API FUNCTIONS
# ==============================================================================
def xa_load(pModuleid):
    """Loads a module"""
    if gModulesLoading:
        es.loadModuleAddon('xa/modules/%s' % pModuleid)

def xa_unload(pModuleid):
    """Unloads a module"""
    if gModulesLoading:
        es.unload('xa/modules/%s' % pModuleid)

def xa_reload(pModuleid):
    """Reloads a module"""
    if gModulesLoading:
        es.unload('xa/modules/%s' % pModuleid)
        gamethread.queue(es.loadModuleAddon, ('xa/modules/%s' % pModuleid,))

def xa_runconfig():
    """Runs XA's configuration file"""
    setting.executeConfiguration(None)

def debug(dbglvl, message):
    """Debugs a message"""
    if int(gCoreVariables['debug']) >= dbglvl:
        es.dbgmsg(0, message)

def register(pModuleid):
    """Registers a new module with XA"""
    gModules[pModuleid] = Admin_module(pModuleid)
    es.dbgmsg(0, '[eXtensible Admin] Registered module "%s"' % gModules[pModuleid].name)
    return gModules[pModuleid]

def unregister(pModuleid):
    """Unregisters the module from XA"""
    if exists(pModuleid):
        module = find(pModuleid)
        if module.required:
            es.dbgmsg(0, '[eXtensible Admin] ***********************************')
            es.dbgmsg(0, '[eXtensible Admin] WARNING! Module "%s" is required!' % module.name)
            for submodule in module.requiredFrom:
                submodule = find(submodule)
                if submodule.name in modules():
                    es.dbgmsg(0, '[eXtensible Admin] Required by "%s"' % submodule.name)
                else:
                    module.required -= 1
                    module.requiredFrom.remove(submodule.name)
            es.dbgmsg(0, '[eXtensible Admin] ***********************************')
        for submodule in module.requiredList:
            if submodule in modules():
                submodule = find(submodule)
                submodule.required -= 1
                submodule.requiredFrom.remove(module.name)
                module.required -= 1
                module.requiredList.remove(submodule.name)
        for command in module.subCommands:
            module.delCommand(command)
        for menu in module.subMenus:
            module.delMenu(menu)
        es.dbgmsg(0, '[eXtensible Admin] Unregistered module "%s"' % module.name)
        del gModules[module.name]

def modules():
    """Returns the list of registered modules"""
    return gModules.keys()
    
def corevars():
    """Returns the list of core server variables"""
    return gCoreVariables.values()

def exists(pModuleid):
    """Checks if the module is registered with XA Core"""
    return str(pModuleid) in modules()

def find(pModuleid):
    """Returns the class instance of the named module"""
    if exists(pModuleid):
        return gModules[str(pModuleid)]

def isRequired(pModuleid):
    """Checks if the module is required by other modules"""
    if exists(pModuleid):
        return bool(find(pModuleid).required)

def findMenu(pModuleid, pMenuid):
    """Returns the class instance a menu in the named module"""
    if exists(pModuleid):
        if pMenuid in find(pModuleid).subMenus:
            return find(pModuleid).subMenus[pMenuid]

def findCommand(pModuleid, pCommandid):
    """Returns the class instance a command in the named module"""
    if exists(pModuleid):
        if pCommandid in find(pModuleid).subCommands:
            return find(pModuleid).subCommands[pCommandid]

def isManiMode():
    """Checks if Mani mode is enabled"""
    return bool(int(gCoreVariables['manimode']))

def getLevel(auth_capability):
    """Returns the Auth Provider level by name"""
    return cmdlib.permissionToInteger(auth_capability)

def registerCapability(auth_capability, auth_recommendedlevel):
    """Registers an auth capability with the recommended level"""
    return services.use('auth').registerCapability(auth_capability, getLevel(auth_recommendedlevel))

def isUseridAuthorized(auth_userid, auth_capability):
    """Checks if a userid is authorized or not"""
    return services.use('auth').isUseridAuthorized(auth_userid, auth_capability)

def sendMenu(userid=None, choice=10, name=None):
    """Shows the main menu to the specified player"""
    if choice != 10:
        return None
    if userid:
        userid = int(userid)
    elif es.getcmduserid():
        userid = int(es.getcmduserid())
    if userid and (es.exists('userid', userid)):
        gMainMenu[userid] = popuplib.easymenu('xa_%s'%userid, None, incomingMenu)
        gMainMenu[userid].settitle(language.createLanguageString(None, 'eXtensible Admin'))
        gMainMenu[userid].vguititle = 'eXtensible Admin'
        for module in modules():
            module = find(module)
            for page in module.subMenus:
                if module.subMenus[page] and not module.subMenus[page].permission or isUseridAuthorized(userid, module.subMenus[page].permission):
                    gMainMenu[userid].addoption(page, module.subMenus[page].display, 1)
        if popuplib.active(userid)['name'] == gMainMenu[userid].name or popuplib.isqueued(gMainMenu[userid].name, userid):
            gMainMenu[userid].update(userid)
        else:
            gMainMenu[userid].send(userid)

def incomingMenu(userid, choice, name):
    for module in modules():
        module = find(module)
        if choice in module.subMenus:
            if module.subMenus[choice] and not module.subMenus[choice].permission or isUseridAuthorized(userid, module.subMenus[choice].permission):
                module.subMenus[choice].menuobj.send(userid)

def addondir():
    return str(es.ServerVar('eventscripts_addondir')).replace("\\", "/")

def gamedir():
    return str(es.ServerVar('eventscripts_gamedir')).replace("\\", "/")

def coredir():
    return str(es.getAddonPath('xa')).replace("\\", "/")

def moduledir(pModuleid):
    return str('%smodules/%s' % (es.getAddonPath('xa'), pModuleid)).replace("\\", "/")

def copytree(src, dst, counter=0):
    # modified Python 2.6 shutil.copytree method that ignores existing files
    if not os.path.exists(dst):
        os.makedirs(dst)
    for name in os.listdir(src):
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        if os.path.isdir(srcname):
            counter += copytree(srcname, dstname, counter)
        elif not os.path.exists(dstname):
            shutil.copy2(srcname, dstname)
            counter += 1
    try:
        shutil.copystat(src, dst)
    except:
        pass # can't copy file access times on Windows
    return counter

# ==============================================================================
#   GAME EVENTS
# ==============================================================================
def load():
    global gMainConfig, gMainMenu, gMainCommand, gModulesLoading
    es.dbgmsg(0, '[eXtensible Admin] Second loading part...')
    if not services.isRegistered('auth'):
        es.dbgmsg(0, '[eXtensible Admin] WARNING! Auth Provider required!')
        es.dbgmsg(0, '[eXtensible Admin] Loading Mani Basic Auth...')
        es.load('examples/auth/mani_basic_auth')
    gMainCommand = Admin_command('xa', command)
    gMainCommand.register(['server', 'console', 'say'])
    gModulesLoading = False
    es.dbgmsg(0, '[eXtensible Admin] Merging default configuration...')
    gCopiedFiles = copytree('%s/cfg/xa/_defaults' % gamedir(), '%s/cfg' % gamedir())
    es.dbgmsg(0, '[eXtensible Admin] Number of files copied = %d' % gCopiedFiles)
    es.dbgmsg(0, '[eXtensible Admin] Executing xa.cfg...')
    gMainConfig = cfglib.AddonCFG('%s/cfg/xa.cfg' % gamedir())
    gMainConfig.execute()
    es.dbgmsg(0, '[eXtensible Admin] Mani mode enabled = %s' % isManiMode())
    gModulesLoading = True
    if isManiMode():
        ma = Admin_mani()
        es.dbgmsg(0, '[eXtensible Admin] Executing mani_server.cfg...')
        ma.loadVariables()
        es.server.cmd('es_xmexec mani_server.cfg')
        ma.hookAuthProvider()
    es.dbgmsg(0, '[eXtensible Admin] Third loading part...')
    es.dbgmsg(0, '[eXtensible Admin] Executing xa.cfg...')
    gMainConfig.execute()
    es.dbgmsg(0, '[eXtensible Admin] Executing xamodules.cfg...')
    setting.executeConfiguration(None)
    es.dbgmsg(0, '[eXtensible Admin] Updating xamodules.cfg...')
    setting.writeConfiguration(None)
    es.dbgmsg(0, '[eXtensible Admin] Finished loading')

def unload():
    global gMainMenu, gMainCommand
    es.dbgmsg(0, '[eXtensible Admin] Begin unloading...')
    for module in sorted(gModules.values(), lambda x, y: cmp(x.required, y.required)*-1):
        for command in module.subCommands:
            module.subCommands[command].unregister(['console', 'say'])
        for menu in module.subMenus:
            module.subMenus[menu].unregister()
        es.dbgmsg(0, '[eXtensible Admin] Unloading module "%s"' % module.name)
        module.unload()
    for menu in gMainMenu:
        if popuplib.exists(str(menu)):
            menu.delete()
    if gMainCommand:
        gMainCommand.unregister(['server', 'console', 'say'])
        del gMainCommand
    es.dbgmsg(0, '[eXtensible Admin] Finished unloading sequence')
    es.dbgmsg(0, '[eXtensible Admin] Modules will now unregister themself...')

# ==============================================================================
#   SERVER COMMANDS
# ==============================================================================
def command(userid, args):
    if userid > 0:
        return sendMenu()
    else:
        argc = len(args)
        subcmd = (args[0].lower() if argc else None)
        seccmd = (args[1] if argc > 1 else None)
    if subcmd == 'load':
        if seccmd:
            xa_load(seccmd)
        else:
            es.dbgmsg(0, 'Syntax: xa load <module-name>')
    elif subcmd == 'unload':
        if seccmd:
            xa_unload(seccmd)
        else:
            es.dbgmsg(0, 'Syntax: xa unload <module-name>')
    elif subcmd == 'reload':
        if seccmd:
            xa_reload(seccmd)
        else:
            es.dbgmsg(0, 'Syntax: xa reload <module-name>')
    elif subcmd == 'send':
        if seccmd:
            sendMenu(seccmd)
        else:
            es.dbgmsg(0, 'Syntax: xa send <userid>')
    elif subcmd == 'help':
        helplist = {}
        if exists(seccmd):
            module = find(seccmd)
            for command in sorted(module.subCommands):
                helplist[command] = ['cmd', str(module.subCommands[command].permission), str(module.subCommands[command].descr)]
            for variable in sorted(module.variables):
                helplist[variable] = ['var', str(module.variables[variable]), str(module.variables[variable]._def), str(module.variables[variable]._descr)]
        else:
            for module in sorted(modules()):
                module = find(module)
                for command in sorted(module.subCommands):
                    helplist[command] = ['cmd', str(module.subCommands[command].permission), str(module.subCommands[command].descr)]
                for variable in sorted(module.variables):
                    helplist[variable] = ['var', str(module.variables[variable]), str(module.variables[variable]._def), str(module.variables[variable]._descr)]
        es.dbgmsg(0,'---------- List of commands and variables:')
        for helpindex in sorted(helplist):
            helpline = helplist[helpindex]
            if helpline[0] == 'cmd':
                es.dbgmsg(0,('%-*s'%(40, helpindex))+' : '+('%-*s'%(8, 'cmd'))+' : '+('%-*s'%(16, helpline[1]))+' : '+helpline[2])
            elif helpline[0] == 'var':
                es.dbgmsg(0,('%-*s'%(40, helpindex))+' : '+('%-*s'%(8, helpline[1]))+' : '+('%-*s'%(16, helpline[2]))+' : '+helpline[3])
        es.dbgmsg(0,'----------')
        es.dbgmsg(0, 'Syntax: xa help [module]')
    elif subcmd == 'permissions':
        permissions = []
        if seccmd:
            userid = int(es.getuserid(seccmd))
        else:
            userid = None
        if userid:
            permissions.append(['Module', 'Capability', 'Level', 'Type', 'Name', 'Granted'])
        else:
            permissions.append(['Module', 'Capability', 'Level', 'Type', 'Name'])
        for module in sorted(modules()):
            module = find(module)
            if userid:
                for command in sorted(module.subCommands):
                    permissions.append([str(module.name), str(module.subCommands[command].permission), str(module.subCommands[command].permissionlevel), 'command', str(module.subCommands[command].name), module.isUseridAuthorized(userid, str(module.subCommands[command].permission))])
                for menu in module.subMenus:
                    permissions.append([str(module.name), str(module.subMenus[menu].permission), str(module.subMenus[menu].permissionlevel), 'menu', str(module.subMenus[menu].name), module.isUseridAuthorized(userid, str(module.subMenus[menu].permission))])
                for custom in module.customPermissions:
                    permissions.append([str(module.name), str(custom), str(module.customPermissions[custom]['level']), 'custom', str(module.customPermissions[custom]['type']), module.isUseridAuthorized(userid, str(custom))])
            else:
                for command in sorted(module.subCommands):
                    permissions.append([str(module.name), str(module.subCommands[command].permission), str(module.subCommands[command].permissionlevel), 'command', str(module.subCommands[command].name)])
                for menu in module.subMenus:
                    permissions.append([str(module.name), str(module.subMenus[menu].permission), str(module.subMenus[menu].permissionlevel), 'menu', str(module.subMenus[menu].name)])
                for custom in module.customPermissions:
                    permissions.append([str(module.name), str(custom), str(module.customPermissions[custom]['level']), 'custom', str(module.customPermissions[custom]['type'])])
        es.dbgmsg(0,'---------- List of capabilities:')
        for perm in permissions:
            if userid:
                if not perm[5] == 'Granted':
                    if perm[5]:
                        granted = 'Yes'
                    else:
                        granted = 'No'
                else:
                    granted = perm[5]
                es.dbgmsg(0,('%-*s'%(18, perm[0]))+' '+('%-*s'%(20, perm[1]))+' '+('%-*s'%(8, '['+perm[2]+']'))+' '+('%-*s'%(10, perm[3]))+' '+('%-*s'%(15, perm[4]))+' '+granted)
            else:
                es.dbgmsg(0,('%-*s'%(18, perm[0]))+' '+('%-*s'%(20, perm[1]))+' '+('%-*s'%(8, '['+perm[2]+']'))+' '+('%-*s'%(10, perm[3]))+' '+perm[4])
        es.dbgmsg(0,'----------')
        es.dbgmsg(0, 'Syntax: xa permissions [user]')
    elif subcmd == 'stats':
        statistics = []
        for module in sorted(modules()):
            module = find(module)
            xlibs = xfuncs = xcalls = xsubcalls = xseconds = 0
            for lib in module._xalibs:
                xlibs += 1
                for func in module._xalibs[lib]._xalibfuncs:
                    xfuncs += 1
                    xcalls += module._xalibs[lib]._xalibfuncs[func]._xalibfunccalls
                    xsubcalls += module._xalibs[lib]._xalibfuncs[func]._xalibfuncstats['calls']
                    xseconds += module._xalibs[lib]._xalibfuncs[func]._xalibfuncstats['times']
            statistics.append([str(module.name), xlibs, xfuncs, xcalls, xsubcalls, xseconds])
        es.dbgmsg(0,'---------- List of statistics:')
        if seccmd and seccmd.isdigit():
            sortkey = int(seccmd)
        else:
            sortkey = 5
        if int(gCoreVariables['debugprofile']) > 0:
            sortkey = min(5, sortkey)
        else:
            sortkey = min(3, sortkey)
        sortkey = max(0, sortkey)
        statistics = sorted(statistics, cmp=lambda x,y: cmp(x[sortkey], y[sortkey]))
        statistics.append(['Module', 'Libraries', 'Functions', 'Calls', 'SubCalls', 'CPU seconds'])
        if int(gCoreVariables['debugprofile']) > 0:
            for stat in reversed(statistics):
                es.dbgmsg(0,('%-*s'%(18, stat[0]))+' '+('%-*s'%(10, str(stat[1])))+' '+('%-*s'%(10, str(stat[2])))+' '+('%-*s'%(10, str(stat[3])))+' '+('%-*s'%(10, str(stat[4])))+' '+str(stat[5]))
        else:
            for stat in reversed(statistics):
                es.dbgmsg(0,('%-*s'%(18, stat[0]))+' '+('%-*s'%(10, str(stat[1])))+' '+('%-*s'%(10, str(stat[2])))+' '+str(stat[3]))
        es.dbgmsg(0,'----------')
        es.dbgmsg(0, 'Syntax: xa stats [sort-column]')
    elif subcmd == 'list':
        es.dbgmsg(0,'---------- List of modules:')
        if seccmd and seccmd.isdigit():
            listlevel = int(seccmd)
        else:
            listlevel = 0
        for module in modules():
            module = find(module)
            module.information(listlevel)
        if argc == 2:
            es.dbgmsg(0, ' ')
            es.dbgmsg(0, 'For more details, supply list level (0-2):')
            es.dbgmsg(0, 'Syntax: xa module list [level]')
        es.dbgmsg(0,'----------')
    elif subcmd == 'info':
        if argc >= 2:
            if argc >= 3 and args[2].isdigit():
                listlevel = int(args[2])
            else:
                listlevel = 2
            if exists(seccmd):
                module = find(seccmd)
                module.information(listlevel)
        else:
            es.dbgmsg(0, 'Syntax: xa module info <module-name> [level]')
    else:
        es.dbgmsg(0,'Invalid xa subcommand, see http://python.eventscripts.com/pages/XA for help')
