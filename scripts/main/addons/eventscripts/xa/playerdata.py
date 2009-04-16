# ==============================================================================
#   IMPORTS
# ==============================================================================
# EventScripts Imports
import es
import playerlib
import keyvalues
import xa

# ==============================================================================
#   LOAD PLAYERDATA KEYVALUES OBJECT
# ==============================================================================
gKeyValues = keyvalues.KeyValues(name='playerdata.txt')
gKeyValues.load('%s/data/playerdata.txt' % es.getAddonPath('xa'))

# ==============================================================================
#   HELPER CLASSES
# ==============================================================================
class UserSetting(object):
    def __init__(self, module, pref):
        # Create our setting object
        self.module = str(module)
        self.name = str(pref)
        
        # Does our module exist?
        if self.module in xa.gModules:
            # Add our module tree to the KeyValues tree
            if not self.module in gKeyValues:
                gKeyValues[self.module] = keyvalues.KeyValues(name=self.module)

            # Add our setting tree to the KeyValues tree
            if not self.name in gKeyValues[self.module]:
                gKeyValues[self.module][self.name] = keyvalues.KeyValues(name=self.name)

    def __str__(self):
        # Return a printable string
        return self.name

    def __repr__(self):
        # Return something that represents our object
        return 'UserSetting(%s)' % self.name

    def exists(self, userid):
        # Get the userid's uniqueid
        steamid = playerlib.uniqueid(userid, True)
        
        # Return if our user's setting has a value
        return steamid in gKeyValues[self.module][self.name]

    def set(self, userid, value):
        # Get the userid's uniqueid
        steamid = playerlib.uniqueid(userid, True)
        
        # Set the user's setting to the new value
        gKeyValues[self.module][self.name][steamid] = value
        
        # Return if our user's setting has the new value
        return gKeyValues[self.module][self.name][steamid] == value
        
    def get(self, userid):
        # Check if our user's setting has a value
        if self.exists(userid):
            # Get the userid's uniqueid
            steamid = playerlib.uniqueid(userid, True)

            # Return the user's setting value
            return gKeyValues[self.module][self.name][steamid]

# ==============================================================================
#   MODULE API FUNCTIONS
# ==============================================================================
def createUserSetting(module, pref):
    # Create a new setting object
    return UserSetting(module, pref)

def saveUserSetting(module):
    # Save all user settings
    gKeyValues.save('%s/data/playerdata.txt' % es.getAddonPath('xa'))
