import es
import xa
import xa.setting
import xa.logging

#######################################
# ADDON INFORMATION
# This describes the XA module
info = es.AddonInfo()
# TODO: Change this to your module's data.  -- TODO
info.name           = "XA:Sample"
info.version        = "0.1"
info.author         = "New Scripter"
info.url            = "http://forums.mattie.info/"
info.description    = "Sample XA Module"


#######################################
# MODULE NAME
# This is the name of the module.
# TODO: Change this to your module name.    -- TODO
mymodulename = "mymodule"
# Register the module
# this is a global reference to our module
mymodule = xa.register(mymodulename)


#######################################
# SERVER VARIABLES
# The list of our server variables
# TODO: Add your own variables              -- TODO
myvariable = xa.setting.createVariable('some_variable', 1, "XA: Some variable (1=on, 0=off)")


#######################################
# GLOBALS
# Initialize our general global data here.
# Localization helper:
text = xa.language.getLanguage(mymodulename)


#######################################
# LOAD AND UNLOAD
# Formal system registration and unregistration
def load():
    xa.logging.log(mymodule, "XA module %s loaded." % mymodulename)
    # TODO: Register menu, say, client, or console commands.
    #                                       -- TODO


def unload():
    xa.logging.log(mymodule, "XA module is %s being unloaded." % mymodulename)
    # Unregister the module
    xa.unregister(mymodulename)


#######################################
# MODULE FUNCTIONS
# Register your module's functions
