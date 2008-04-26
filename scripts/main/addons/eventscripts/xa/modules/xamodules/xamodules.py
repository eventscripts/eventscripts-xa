import es
import popuplib
from os import listdir,path
from xa import xa

info = es.AddonInfo()
info.name = 'xamodules'
info.version = '1.0.1'
info.basename = 'xa/modules/xamodules'
info.author = 'british.assassin'

xamodules = xa.register('xamodules')
xalanguage = xamodules.language.getLanguage()

gGamedir = str(es.ServerVar('eventscripts_gamedir')).replace('\\','/')
gMenus = {'load':{},'unload':{},'reload':{}}

def load():
    global gModules
    gModules = filter(filter_modules,listdir(gGamedir + '/addons/eventscripts/xa/modules'))
    xamodulesmenu = popuplib.easymenu('xamodulesmenu',None,xamodulesmenu_handler)
    xamodulesmenu.settitle(xalanguage['module management'])
    xamodulesmenu.addoption('load_module',xalanguage['load module'])
    xamodulesmenu.addoption('unload_module',xalanguage['unload module'])
    xamodulesmenu.addoption('reload_module',xalanguage['reload module'])
    xamodules.addMenu('xamodulesmen',xalanguage['module management'],'xamodulesmenu','manage_modules','#root')

def unload():
    xamodules.unregister()

def filter_modules(module):
    return path.isdir(gGamedir + '/addons/eventscripts/xa/modules/' + module)

def xamodulesmenu_handler(userid,choice,popupid):
    if choice == 'load_module':
        if userid in gMenus['load']:
            gMenus['load'][userid].delete()
        for module in xa.gModules:
            if xa.gModules[module].name in gModules:
                gModules.remove(xa.gModules[module].name)
        gMenus['load'][userid] = popuplib.easymenu('xaloadmodule_%s' %userid,None,xaloadmodule_handler)
        gMenus['load'][userid].settitle(xalanguage['load module'])
        for module in gModules:
            gMenus['load'][userid].addoption(module,module)
        gMenus['load'][userid].send(userid)
    elif choice == 'unload_module':
        if userid in gMenus['unload']:
            gMenus['unload'][userid].delete()
        gMenus['unload'][userid] = popuplib.easymenu('xaunloadmodule_%s' %userid,None,xaunloadmodule_handler)
        gMenus['unload'][userid].settitle(xalanguage['unload module'])
        for module in xa.gModules:
            gMenus['unload'][userid].addoption(module,module)
        gMenus['unload'][userid].send(userid)
    elif choice == 'reload_module':
        if userid in gMenus['reload']:
            gMenus['reload'][userid].delete()
        gMenus['reload'][userid] = popuplib.easymenu('xareloadmodule_%s' %userid,None,xareloadmodule_handler)
        gMenus['reload'][userid].settitle(xalanguage['reload module'])
        for module in xa.gModules:
            gMenus['reload'][userid].addoption(module,module)
        gMenus['reload'][userid].send(userid)

def xaloadmodule_handler(userid,choice,popupid):
    xa.xa_load(choice)

def xaunloadmodule_handler(userid,choice,popupid):
    xa.xa_unload(choice)

def xareloadmodule_handler(userid,choice,popupid):
    xa.xa_reload(choice)