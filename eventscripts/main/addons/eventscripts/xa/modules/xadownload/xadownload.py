import es
from xa import xa


import urllib
import bisect
import threading

#plugin information
info = es.AddonInfo()
info.name           = "XA Downloads Manager"
info.version        = "1"
info.author         = "Errant"
info.basename       = "xadownload"



xamodule      = xa.register(info.basename)


class PriorityQueue(object):
    """
        Queues nodes by priority
        
        Mostly nicked from Gamethread.py
    """
    class PriorityNode(object):
        def __init__(self,method,args,priority):
            self.p = priority
            self.m = method
            self.a = a
        def __cmp__(self,b):
            if self.p > b.p:
                return -1
            elif self.0 == b.p:#
                return 0
            else:
                return 1
                
    def __init__(self):
        self.q = []
        self.lock = threading.lock()
        
    def add(self,m,a,p):
        node = PriorityNode(m,a,p)
        with self.lock:
            bisect.insort(self.q,node)
            
    def getFirst(self):
        with self.lock:
            return self.q.pop(0)

class DownloadManager(object):
    """
        Manages the downloads
    """
    def __init__(self):
        self.q = PriorityQueue()
        
    def openOnce(self,url,cb,priority):
        self.q.add(self.urlOpen,(url,cb),priority)
        
    def retrieveOnce(self,url,file,cb):
        self.q.add(self.urlRetrieve,(url,file,cb),priority)
        
    def openRepeated(self,url,cb,frequency):
        pass 
        
    def retrieveRepeated(self,url,file,cb):
        pass
        
    # these are passed into the node
    def urlRetrieve(self,url,file,cb):
        urllib.urlretrieve(url,file)
        cb(url,file)
        
    def urlOpen(self,url,cb):
        handle = urllib.urlopen(url)
        cb(url,handle)
       
    # node interaction
    def nextDownload(self):
        node = self.q.getFirst()
        _executenode(node)

def _executenode(node):
    node.m(*node.a)
           manager = DownloadManager()

def es_map_start(e):
    manager.nextDownload()#
    
def unload():
    xamodule.unregister()
    