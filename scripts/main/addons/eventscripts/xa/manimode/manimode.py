import es

import psyco
psyco.full()

manimode = es.ServerVar("xa_manimode")

def load():
    manimode = 1

def unload():
    manimode = 0
