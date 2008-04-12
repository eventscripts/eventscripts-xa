import es
import services
import popuplib
import langlib
import random
from xa import xa

info = es.AddonInfo()
info.name        = "Config"
info.version     = "0.1"
info.author      = "Hunter"
info.url         = "http://forums.mattie.info/cs/forums/index.php"
info.description = "Popup interface for XA configuration"

xaconfig = xa.register('xaconfig')
lang = xaconfig.language.getLanguage()
auth = services.use('auth')
menulist = []

def load():
    global menulist,mainmenu
    xacmd = xaconfig.addCommand('xa_config', _sendmain, 'change_config', '#root')
    xacmd.register('say')  

    auth.registerCapability("setconfig", auth.ROOT)  
    if not int(es.exists('clientcommand','setconfig')):
        es.regclientcmd('setconfig','xa/modules/xaconfig/inputbox_handle', 'Set config')  
	
    mainmenu = popuplib.easymenu('xamainconfigmenu',None,_mainmenu_select)
    mainmenu.settitle(lang['main config'])
    mainmenu.addoption('core', lang['core config'])
    mainmenu.addoption('module', lang['module config'])
    menulist.append(mainmenu)
    xaconfig.addMenu('xamainconfigmenu',lang['xa menu choice'],'xamainconfigmenu','change_config','#root')
	
def unload():
    global menulist
    for menu in menulist:
        if popuplib.exists(str(menu)): 
            popuplib.delete(str(menu))
    es.unregclientcmd('setconfig')
    xa.unregister('xaconfig')
    
def _moduleListMenu(userid):
    modulemenu = popuplib.easymenu('xalistmodulemenu_'+str(userid),None,_modulemenu_select)
    modulemenu.settitle(lang['module overview'])
    modulemenu.submenu(mainmenu)
    menulist.append(modulemenu)
    modulelist = xa.gModules.keys()
    for module in sorted(modulelist):
        if len(xa.gModules[str(module)].variables) > 0:
            for ll in langlib.getLanguages():
                modulemenu.addoption(str(module), str(module),1,langlib.getLangAbbreviation(ll))
    return modulemenu

def _variableListMenu(userid, module, parent):
    varlist = xa.setting.getVariables(module)
    varmenu = popuplib.easymenu('xalistsettingmenu_'+str(userid)+'_'+str(module),None,_varmenu_select)
    varmenu.settitle(lang['module variables'])
    varmenu.submenu(parent)
    varmenu._xa = [module, parent]
    menulist.append(varmenu)
    for var in sorted(varlist):
        value = str(var)
        if len(value) > 10:
            value = value[0:10]
        for ll in langlib.getLanguages():
            varmenu.addoption(str(var.getName()), str(var.getName())+' = '+str(value),1,langlib.getLangAbbreviation(ll))
    return varmenu
    
def _variableCoreListMenu(userid, parent):
    varlist = xa.gCoreVariables
    varmenu = popuplib.easymenu('xalistsettingmenu_'+str(userid)+'_core',None,_varmenu_select)
    varmenu.settitle(lang['core variables'])
    varmenu.submenu(parent)
    varmenu._xa = ['core', parent]
    menulist.append(varmenu)
    for var in sorted(varlist):
        var._def = str(var)
        var._descr = 'Core variable'
        value = str(var)
        if len(value) > 10:
            value = value[0:10]
        for ll in langlib.getLanguages():
            varmenu.addoption(str(var.getName()), str(var.getName())+' = '+str(value),1,langlib.getLangAbbreviation(ll))
    return varmenu

def _variableEditMenu(userid, module, variable, parent):
    if str(module) != 'core':
        descr = str(variable._descr)
        if len(descr) > 100:
            descr = descr[0:50] + '\n' + descr[50:50] + '\n' + descr[100:50]
        elif len(descr) > 50:
            descr = descr[0:50] + '\n' + descr[50:50]
    changesetting = popuplib.create('xachangesettingmenu_'+str(random.randint(1, 10))+'_'+str(userid)+'_'+variable.getName())
    changesetting.addline(lang('change setting'))
    changesetting.addlineAll('Name: '+variable.getName())
    changesetting.addlineAll('Value: '+str(variable))
    if str(module) != 'core':
        changesetting.addlineAll(descr)
        changesetting.addlineAll(' ')
        changesetting.addline(lang('variable warning'))
    changesetting.addlineAll('------------------------------------')
    changesetting.addline(popuplib.langstring('->1. ',lang['type value']))
    changesetting.addline(popuplib.langstring('->2. ',lang['default value']))
    changesetting.addlineAll('------------------------------------')
    if str(variable).isdigit():
        changesetting.addlineAll('->3. +1')
        changesetting.addlineAll('->4. -1')
        changesetting.addlineAll('->5. +10')
        changesetting.addlineAll('->6. -10')
        changesetting.addlineAll('->7. +100')
        changesetting.addlineAll('->8. -100')
        changesetting.addlineAll('------------------------------------')
        changesetting._xatype = 'int'
    elif str(variable).replace('.', '').isdigit():
        changesetting.addlineAll('->3. +0.1')
        changesetting.addlineAll('->4. -0.1')
        changesetting.addlineAll('->5. +1.0')
        changesetting.addlineAll('->6. -1.0')
        changesetting.addlineAll('->7. +10.0')
        changesetting.addlineAll('->8. -10.0')
        changesetting.addlineAll('------------------------------------')
        changesetting._xatype = 'float'
    else:
        changesetting._xatype = 'str'
    if str(module) != 'core':
        changesetting.addline(popuplib.langstring('->9. ',lang['save back']))
    changesetting.addline(popuplib.langstring('0. ',lang['just back']))
    changesetting.menuselect = _changesetting_select
    changesetting._xa = [module, variable, parent]
    menulist.append(changesetting)
    return changesetting

def _sendmain():
    userid = es.getcmduserid()
    if auth.isUseridAuthorized(userid, 'xaconfig'):
        mainmenu.send(userid)
        
def _mainmenu_select(userid,choice,popupid):
    if choice == 'core':
        menu = _variableCoreListMenu(userid, popupid)
        menu.send(userid)
    elif choice == 'module':
        menu = _moduleListMenu(userid)
        menu.send(userid)

def _modulemenu_select(userid,choice,popupid):
    if xa.exists(choice):
        module = xa.find(choice)
        menu = _variableListMenu(userid, module, popupid)
        menu.send(userid)

def _varmenu_select(userid,choice,popupid):
    if es.exists('variable', choice):
        parentmenu = popuplib.find(popupid)
        parent = parentmenu._xa[0]
        if str(parent) != 'core':
            if choice in xa.gModules[str(parent)].variables:
                var = xa.gModules[str(parent)].variables[choice]
                menu = _variableEditMenu(userid, parent, var, popupid)
                menu.send(userid)
        else:
            for var in xa.gCoreVariables:
                if var.getName() == choice:
                    menu = _variableEditMenu(userid, parent, var, popupid)
                    menu.send(userid)

def _changesetting_select(userid,choice,popupid):
    menu = popuplib.find(popupid)
    module = menu._xa[0]
    variable = menu._xa[1]
    parent = menu._xa[2]
    if int(choice) == 1:
        _setconfig_handle(userid, module, variable, parent)
    elif int(choice) == 2:
        variable.set(variable._def)
        menu = _variableEditMenu(userid, module, variable, parent)
        menu.send(userid)
    elif (int(choice) > 2) and (int(choice) < 9):
        if menu._xatype == 'int':
            value = int(variable)
            if int(choice) == 3:
                variable.set(value+1)
            elif int(choice) == 4:
                variable.set(value-1)
            elif int(choice) == 5:
                variable.set(value+10)
            elif int(choice) == 6:
                variable.set(value-10)
            elif int(choice) == 7:
                variable.set(value+100)
            elif int(choice) == 8:
                variable.set(value-100)
            menu = _variableEditMenu(userid, module, variable, parent)
            menu.send(userid)
        elif menu._xatype == 'float':
            value = float(variable)
            if int(choice) == 3:
                variable.set(value+0.1)
            elif int(choice) == 4:
                variable.set(value-0.1)
            elif int(choice) == 5:
                variable.set(value+1.0)
            elif int(choice) == 6:
                variable.set(value-1.0)
            elif int(choice) == 7:
                variable.set(value+10.0)
            elif int(choice) == 8:
                variable.set(value-10.0)
            menu = _variableEditMenu(userid, module, variable, parent)
            menu.send(userid)
        else:
            popuplib.send(popupid, userid)
    elif int(choice) == 9:
        xa.setting.saveVariables()
        parent = popuplib.find(parent)
        if str(module) != 'core':
            newparent = _variableListMenu(userid, module, str(parent._xa[1]))
        else:
            newparent = _variableCoreListMenu(userid, str(parent._xa[1]))
        newparent.send(userid)
    else:
        parent = popuplib.find(parent)
        if str(module) != 'core':
            newparent = _variableListMenu(userid, module, str(parent._xa[1]))
        else:
            newparent = _variableCoreListMenu(userid, str(parent._xa[1]))
        newparent.send(userid)
    
def _setconfig_handle(userid, module, var, parent):
    if auth.isUseridAuthorized(userid, 'setconfig'):
        es.escinputbox(30,userid,"Change '"+str(var.getName())+"' setting"+'\n \nCurrent value: '+str(var)+'\nDefault value: '+str(var._def)+'\n \n'+str(var._descr),'Type in the new value:','setconfig '+str(parent)+' '+str(module)+' '+str(var.getName()))

def inputbox_handle():
    userid = es.getcmduserid()
    count = int(es.getargc())
    if count > 4:
        parent = es.getargv(1)
        if popuplib.exists(parent):
            module = es.getargv(2)
            if module in xa.gModules:
                varname = es.getargv(3)
                if varname in xa.gModules[module].variables:
                    var = xa.gModules[module].variables[varname]
                    i = 4
                    newvalue = ''
                    while i < count:
                        newvalue = newvalue+' '+es.getargv(i)
                        i = i + 1
                    newvalue = newvalue.strip()
                    var.set(newvalue)
                    es.esctextbox(10, userid, "Changed '"+str(varname)+"' setting", "Changed '%s' to '%s'\nThe variable menu is open again.\nPress [ESC] a second time." %(varname,newvalue))
                    menu = _variableEditMenu(userid, module, var, parent)
                    menu.send(userid)
    else:
        es.esctextbox(10, userid, "Invalid Entry", "<value>")
