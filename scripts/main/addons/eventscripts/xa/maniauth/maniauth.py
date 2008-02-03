import es
import services
import services.auth
import os
import keyvalues

import psyco
psyco.full()

#plugin information
info = es.AddonInfo()
info.name = "Mani clients.txt Auth Provider"
info.version = "0.1"
info.author = "Hunter"
info.url = "http://forums.mattie.info/"
info.description = "Auth Provider that uses Mani's clients.txt"
info.tags = "admin clients XA"

selfaddondir = str(es.server_var["eventscripts_addondir"]).replace("\\", "/")
selfmoddir = str(selfaddondir).rsplit("/", 2)[0] + '/'

def load():
  mani_auth = ManiAuthService()
  services.register("auth", mani_auth)

def unload():
  services.unregister("auth")
  
class ManiAuthService(services.auth.AuthorizationService):
  def __init__(self):
    self.defaultlevels = {}
    self.assignedlevels = {}
    self.aliaslevels = keyvalues.KeyValues(name="manipermission.txt")
    if os.path.exists(selfaddondir+"/xa/static/manipermission.txt"):
      self.aliaslevels.load(selfaddondir+"/xa/static/manipermission.txt")
    self.filename = selfmoddir+'cfg/mani_admin_plugin/clients.txt'
    self.keyvalues = keyvalues.KeyValues(name="clients.txt")
    if os.path.exists(self.filename):
      self.keyvalues.load(self.filename)
    if not "players" in self.keyvalues:
      self.keyvalues["players"] = keyvalues.KeyValues(name="players")
    if not "admingroups" in self.keyvalues:
      self.keyvalues["admingroups"] = keyvalues.KeyValues(name="admingroups")
    if not "immunitygroups" in self.keyvalues:
      self.keyvalues["immunitygroups"] = keyvalues.KeyValues(name="immunitygroups")

  def registerCapability(self, auth_capability, auth_recommendedlevel):
    self.defaultlevels[auth_capability] = int(auth_recommendedlevel)
    return
    
  def isUseridAuthorized(self, auth_userid, auth_capability, auth_type="admin"):
    user = self.getOfflineIdentifier(auth_userid)
    data = self.isIdAuthorized(user, auth_capability, auth_type)
    return data
    
  def getOfflineIdentifier(self, auth_userid):
    s = es.getplayersteamid(int(auth_userid))
    if s is None:
      raise KeyError, "The userid is not online."
    return s
  
  def isIdAuthorized(self, auth_identifier, auth_capability, auth_type="admin"):

    if auth_identifier is None:
      return False

    if auth_capability in self.aliaslevels:
        auth_flag = self.aliaslevels[auth_capability]
    else:
        auth_flag = auth_capability

    # Admins always win
    if (str(auth_type) != "admin") and (str(auth_type) != "immunity"):
      auth_type = "admin"
    for user in self.keyvalues["players"]:
      if auth_identifier == str(self.keyvalues["players"][str(user)]["steam"]):
        auth_keyvalues = self.keyvalues["players"][str(user)]
        if str(auth_type)+"flags" in auth_keyvalues:
          for flaglist in auth_keyvalues[str(auth_type)+"flags"]:
            for flag in str(auth_keyvalues[str(auth_type)+"flags"][str(flaglist)]).split(" "):
              if (auth_capability == str(flag)) or (auth_flag == str(flag)):
                return True
        if (str(auth_type)+"groups" in auth_keyvalues) and (str(auth_type)+"groups" in self.keyvalues):
          for group in str(auth_keyvalues[str(auth_type)+"groups"]).split(" "):
            if group in self.keyvalues[str(auth_type)+"groups"]:
              for flag in str(self.keyvalues[str(auth_type)+"groups"][str(group)]).split(" "):
                if (auth_capability == str(flag)) or (auth_flag == str(flag)):
                  return True
        return False

    # if it's not registered, no way!
    if not self.defaultlevels.has_key(auth_capability):
      return False
      
    level = self.defaultlevels[auth_capability]
    # Allow it if unrestricted
    if level >= self.UNRESTRICTED:
      return True
      
    # If they have to be identified, require that their steamid is ready.
    if level >= self.IDENTIFIED and str(auth_identifier) != "STEAM_ID_PENDING":
      return True
    
    # Check if any other user has the cap
    # pre-check
    if auth_capability in self.assignedlevels:
      if self.assignedlevels[auth_capability] == True:
        return False
    # scan-check
    for user in self.keyvalues["players"]:
      if auth_identifier != str(self.keyvalues["players"][str(user)]["steam"]):
        auth_keyvalues = self.keyvalues["players"][str(user)]
        if "immunityflags" in auth_keyvalues:
          for flaglist in auth_keyvalues["immunityflags"]:
            for flag in str(auth_keyvalues["immunityflags"][str(flaglist)]).split(" "):
              if (auth_capability == str(flag)) or (auth_flag == str(flag)):
                self.assignedlevels[auth_capability] = True
                return False
        if ("immunitygroups" in auth_keyvalues) and ("immunitygroups" in self.keyvalues):
          for group in str(auth_keyvalues["immunitygroups"]).split(" "):
            if group in self.keyvalues["immunitygroups"]:
              for flag in str(self.keyvalues["immunitygroups"][str(group)]).split(" "):
                if (auth_capability == str(flag)) or (auth_flag == str(flag)):
                  self.assignedlevels[auth_capability] = True
                  return False
        if "adminflags" in auth_keyvalues:
          for flaglist in auth_keyvalues["adminflags"]:
            for flag in str(auth_keyvalues["adminflags"][str(flaglist)]).split(" "):
              if (auth_capability == str(flag)) or (auth_flag == str(flag)):
                self.assignedlevels[auth_capability] = True
                return False
        if ("admingroups" in auth_keyvalues) and ("admingroups" in self.keyvalues):
          for group in str(auth_keyvalues["admingroups"]).split(" "):
            if group in self.keyvalues["admingroups"]:
              for flag in str(self.keyvalues["admingroups"][str(group)]).split(" "):
                if (auth_capability == str(flag)) or (auth_flag == str(flag)):
                  self.assignedlevels[auth_capability] = True
                  return False

    # #poweruser = immunity
    if level >= self.POWERUSER:
      for user in self.keyvalues["players"]:
        if auth_identifier == str(self.keyvalues["players"][str(user)]["steam"]):
          auth_keyvalues = self.keyvalues["players"][str(user)]
          if "immunityflags" in auth_keyvalues:
            for flaglist in auth_keyvalues["immunityflags"]:
              for flag in str(auth_keyvalues["immunityflags"][str(flaglist)]).split(" "):
                if "immunity" == str(flag).lower():
                  return True
          if ("immunitygroups" in auth_keyvalues) and ("immunitygroups" in self.keyvalues):
            for group in str(auth_keyvalues["immunitygroups"]).split(" "):
              if group in self.keyvalues["immunitygroups"]:
                for flag in str(self.keyvalues["immunitygroups"][str(group)]).split(" "):
                  if "immunity" == str(flag).lower():
                    return True

    # #admin = admin
    if level >= self.ADMIN:
      for user in self.keyvalues["players"]:
        if auth_identifier == str(self.keyvalues["players"][str(user)]["steam"]):
          auth_keyvalues = self.keyvalues["players"][str(user)]
          if "adminflags" in auth_keyvalues:
            for flaglist in auth_keyvalues["adminflags"]:
              for flag in str(auth_keyvalues["adminflags"][str(flaglist)]).split(" "):
                if "admin" == str(flag).lower():
                  return True
          if ("admingroups" in auth_keyvalues) and ("admingroups" in self.keyvalues):
            for group in str(auth_keyvalues["admingroups"]).split(" "):
              if group in self.keyvalues["admingroups"]:
                for flag in str(self.keyvalues["admingroups"][str(group)]).split(" "):
                  if "admin" == str(flag).lower():
                    return True

    # No way, Jose
    return False
