# ./xa/modules/xatimeleft/xatimeleft.py

import es
import time
import xa
import xa.logging
import xa.setting
from xa import xa


float_map_start_time = 0


def load():
    """ """
    xa.logging.log(mymodule, 'xatimeleft loaded')

    mycommand = mymodule.addCommand('timeleft', show_timeleft, 'display_timeleft', '#all')
    mycommand.register(('console', 'say'))


def es_map_start(event_var):
    global float_map_start_time

    float_map_start_time = time.time()


def unload():
    """ """
    xa.logging.log(mymodule, 'xatimeleft unloaded')

    xa.unRegister('xatimeleft')


def timeleft_cmd():
   if not float_map_start_time:
      return # No saved time for this map, so return

   int_userid = es.getcmduserid()
   xa.logging.log(mymodule, 'xatimeleft request by %s (%s)' % (es.getplayersteamid(int_userid), es.getplayername(int_userid)))

   float_mp_timelimit = float(es.ServerVar('mp_timelimit')) * 60
   if float_mp_timelimit:
      float_time_left = float_mp_timelimit - (time.time() - float_map_start_time)
      es.tell(int_userid, 'Time left in map: %s:%s' % (int(float_time_left / 60), int(float_time_left % 60)))
   else:
      es.tell(int_userid, 'No map time limit')