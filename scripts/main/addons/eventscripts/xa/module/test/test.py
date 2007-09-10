import es
import xa
import xa.language
import xa.setting
import xa.playerdata
import xa.mani
import xa.maniconfig
import popuplib
from xa import xa

def load():    
    mymodule = xa.register("test")
    mymodule.addRequirement("anothermodulethatwasalreadyregistered")
    
    mypopup = popuplib.create("mypopup")
    mypopup.addline("Hello World!")
    
    mymenu = mymodule.addMenu("mymenu", "Hello World!!!111oneone", "mypopup", "hello", "#all")
    mymenu.setDisplay("Hello World!")
    
    mycommand = mymodule.addCommand("mycommand", mytestblock, "test_it", "#all")
    mycommand.register(["console","say"])

    myvariable = xa.setting.createVariable(mymodule, "myvariable", "Hello World!", "Should be Hello World!")
    myvariable = xa.setting.getVariable(mymodule, "myvariable")
    
    mykeyvalues = xa.setting.useKeyValues(mymodule)
    mykeyvalues["test"] = "Hello World!"
    xa.setting.saveKeyValues()
    
    myusersetting = xa.playerdata.createUserSetting(mymodule, "testpref")
    xa.playerdata.saveKeyValues()
    
def player_activate(event_var):
    mymodule = xa.find("test")
    myusersetting = xa.playerdata.getUserSetting(mymodule, "testpref")
    myusersetting.set(int(event_var['userid']), "Hello World! Online!")
    xa.playerdata.saveKeyValues()
    
def player_say(event_var):
    mymodule = xa.find("test")
    myusersetting = xa.playerdata.getUserSetting(mymodule, "testpref")
    es.msg(str(myusersetting.get(int(event_var['userid']))))

def player_disconnect(event_var):
    mymodule = xa.find("test")
    myusersetting = xa.playerdata.getUserSetting(mymodule, "testpref")
    myusersetting.set(int(event_var['userid']), "Hello World! Offline!")
    xa.playerdata.saveKeyValues()

def unload():
    xa.unRegister("test")

def mytestblock(userid, command, commandstring, type):
    es.msg("Hello World!")
