import es
import xa
import xa.configparser
import xa.language
import xa.logging
import xa.playerdata
import xa.setting
import xa.manilib
import popuplib
from xa import xa

def load():    
    mymodule = xa.register("unittest")
    mymodule.addRequirement("anothermodulethatwasalreadyregistered")
    
    xa.logging.log(mymodule, "unittest loaded")
    
    mypopup = popuplib.create("mypopup")
    mypopup.addline("Hello World!")
    
    mymenu = mymodule.addMenu("mymenu", "Hello World!!!111oneone", "mypopup", "unittest", "#all")
    mymenu.setDisplay("Hello World!")
    
    mycommand = mymodule.addCommand("mycommand", myunittestblock, "unittest", "#all")
    mycommand.register(["console","say"])

    myvariable = xa.setting.createVariable(mymodule, "myvariable", "Hello World!", "Should be Hello World!")
    myvariable = xa.setting.getVariable(mymodule, "myvariable")
    
    mykeyvalues = xa.setting.useKeyValues(mymodule)
    mykeyvalues["unittest"] = "Hello World!"
    xa.setting.saveKeyValues()
    
    myusersetting = xa.playerdata.createUserSetting(mymodule, "unittestpref")
    xa.playerdata.saveKeyValues()
    
def player_activate(event_var):
    mymodule = xa.find("unittest")
    myusersetting = xa.playerdata.getUserSetting(mymodule, "unittestpref")
    myusersetting.set(int(event_var['userid']), "Hello World! Online!")
    xa.playerdata.saveKeyValues()
    
def player_say(event_var):
    mymodule = xa.find("unittest")
    myusersetting = xa.playerdata.getUserSetting(mymodule, "unittestpref")
    es.msg(str(myusersetting.get(int(event_var['userid']))))

def player_disconnect(event_var):
    mymodule = xa.find("unittest")
    myusersetting = xa.playerdata.getUserSetting(mymodule, "unittestpref")
    myusersetting.set(int(event_var['userid']), "Hello World! Offline!")
    xa.playerdata.saveKeyValues()

def unload():
    xa.logging.log(mymodule, "unittest unloaded")
    xa.unRegister("unittest")

def myunittestblock():
    userid = int(es.getcmduserid())
    es.tell(userid, "Hello World!")
