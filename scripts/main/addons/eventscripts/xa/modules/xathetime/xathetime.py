# ./xa/modules/xathetime/xathetime.py

import es
import time
import xa
import xa.logging
import xa.setting
from xa import xa


mymodule = xa.register('xathetime')
adjust_time = xa.setting.createVariable(mymodule, 'adjust_time', 0, 'Minutes to add to server clock')
military_time = xa.setting.createVariable(mymodule, 'military_time', 0, '0 = use 12hr format, 1 = use 24hr format')
thetime_player_only = xa.setting.createVariable(mymodule, 'thetime_player_only', 1, '0 = time is sent to all players on request, 1 = time is only sent to the requesting player')
thetime_timezone = xa.setting.createVariable(mymodule, 'thetime_timezone', 'GMT', 'Timezone to display -- DOES NOT AFFECT TIME DISPLAYED')


def load():
    """ """
    xa.logging.log(mymodule, 'xathetime loaded')

    mymodule.addCommand('thetime', show_time, 'display_thetime', '#all').register(('console', 'say'))


def unload():
    """ """
    xa.logging.log(mymodule, 'xathetime unloaded')

    xa.unRegister('xathetime')


def show_time():
    """ """
    int_userid = es.getcmduserid()
    xa.logging.log(mymodule, 'xathetime request by %s (%s)' % (es.getplayersteamid(int_userid), es.getplayername(int_userid)))

    tuple_time = time.localtime(time.time() + (60 * int(adjust_time)))
    if int(military_time):
        int_hour = tuple_time[3]
    else:
        int_hour = tuple_time[3] % 12
    str_time = '%s:%02d %s %s-%s-%s' % (int_hour, tuple_time[4], thetime_timezone, tuple_time[2], tuple_time[1], tuple_time[0])

    if int(thetime_player_only):
        es.tell(int_userid, str_time)
    else:
        es.msg(str_time)