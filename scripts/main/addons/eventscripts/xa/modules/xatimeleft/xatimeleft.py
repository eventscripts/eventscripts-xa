# ./xa/modules/xatimeleft/xatimeleft.py

import es
import time
from xa import xa

#######################################
# MODULE NAME
# This is the name of the module.
mymodulename = "xatimeleft"
# Register the module
# this is a global reference to your module
mymodule = xa.register(mymodulename)

float_map_start_time = 0

def load():
    mymodule.logging.log('xatimeleft loaded')

    mymodule.addCommand('timeleft', timeleft_cmd, 'display_timeleft', '#all').register(('console', 'say'))


def es_map_start(event_var):
    global float_map_start_time

    float_map_start_time = time.time()


def unload():
    """ """
    mymodule.logging.log('xatimeleft unloaded')

    xa.unregister(mymodule)


def timeleft_cmd():
   if not float_map_start_time:
      return # No saved time for this map, so return

   int_userid = es.getcmduserid()
   mymodule.logging.log('xatimeleft request by %s (%s)' % (es.getplayersteamid(int_userid), es.getplayername(int_userid)))

   float_mp_timelimit = float(es.ServerVar('mp_timelimit')) * 60
   if float_mp_timelimit:
      float_time_left = float_mp_timelimit - (time.time() - float_map_start_time)
      if float_time_left < 0: float_time_left = 0

      es.tell(int_userid, 'Time left in map: %s:%02d' % (int(float_time_left / 60), int(float_time_left % 60)))

   else:
      es.tell(int_userid, 'No map time limit')
