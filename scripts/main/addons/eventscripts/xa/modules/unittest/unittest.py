import es
import popuplib
from xa import xa

def load():    
    mymodule = xa.register("unittest")
    mymodule.addRequirement("anothermodulethatwasalreadyregistered")
    
    mymodule.logging.log(mymodule, "unittest loaded")
    
    mypopup = popuplib.create("mypopup")
    mypopup.addline("Hello World!")
    
    mymenu = mymodule.addMenu("mymenu", "Hello World!!!111oneone", "mypopup", "unittest", "#all")
    mymenu.setDisplay("Hello World!")
    
    mycommand = mymodule.addCommand("mycommand", myunittestblock, "unittest", "#all")
    mycommand.register(["console","say"])
    
    myusersetting = mymodule.playerdata.createUserSetting(mymodule, "unittestpref")
    mymodule.playerdata.saveKeyValues()
    
def player_activate(event_var):
    mymodule = xa.find("unittest")
    myusersetting = mymodule.playerdata.getUserSetting(mymodule, "unittestpref")
    myusersetting.set(int(event_var['userid']), "Hello World! Online!")
    mymodule.playerdata.saveKeyValues()
    
def player_say(event_var):
    mymodule = xa.find("unittest")
    myusersetting = mymodule.playerdata.getUserSetting(mymodule, "unittestpref")
    es.msg(str(myusersetting.get(int(event_var['userid']))))

def player_disconnect(event_var):
    mymodule = xa.find("unittest")
    myusersetting = mymodule.playerdata.getUserSetting(mymodule, "unittestpref")
    myusersetting.set(int(event_var['userid']), "Hello World! Offline!")
    mymodule.playerdata.saveKeyValues()

def unload():
    mymodule = xa.find("unittest")
    mymodule.logging.log(mymodule, "unittest unloaded")
    mymodule.unregister()

def myunittestblock():
    userid = int(es.getcmduserid())
    es.tell(userid, "Hello World!")
