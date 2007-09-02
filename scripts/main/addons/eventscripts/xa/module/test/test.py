import es
import xa
import popuplib
from xa import xa

def load():
    mypopup = popuplib.create("mypopup")
    mypopup.addline("Hello World!")
    mymodule = xa.register("test")
    mymodule.addRequirement("anothermodulethatwasalreadyregistered")
    mymenu = mymodule.addMenu("mymenu", "Hello World!!!111oneone", "mypopup", "hello", "#all")
    mymenu.setDisplay("Hello World!")
    mycommand = mymodule.addCommand("mycommand", mytestblock, "test_it", "#all")
    mycommand.register(["console","say"])

def unload():
    xa.unRegister("test")

def mytestblock(userid, command, commandstring, type):
    es.msg("Hello World!")
