import xa
import popup
from xa import xa
from popup import popup

def load():
    p = popup.create("votepopup")
    p.addline("Hello World!")
    m = xa.menu_create("votesmenu", "votes", "Vote Management", "votepopup", "voting", "#admin")
    print "Votes! RockZ!"
