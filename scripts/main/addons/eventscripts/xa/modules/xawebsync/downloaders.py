import os
from threading import Thread
import urllib2
from urllib import urlencode
from Queue import Queue 
import gamethread
import es
import time

TEMP_DL_FILE = os.path.join(es.getAddonPath('xa/modules/xawebsync'), '.temp') 


class Response(object):
    def __init__(self, data, success, duration, request):
        self.data       = data
        self.success    = success
        self.duration   = duration
        self.request    = request
        
        
class Request(object):
    def __init__(self, path, data, callback):
        self.path           = path
        self.callback       = callback
        self.data           = data
        self.querystring    = urlencode(data)
        self.start_time     = time.time()
        self.duration       = 0.0
        self.end_time       = 0.0
        
    def get_duration(self):
        self.end_time       = time.time()
        self.duration       = self.end_time - self.start_time
        return self.duration


class Urllib2DownloadManager(object):
    """
    Threaded Urllib2 Download Manager using a single thread.
    """
    class DownloaderThread(Thread):
        def __init__(self, queue):
            es.dbgmsg(1, "Urllib2DownloadManager: Initializing Thread")
            self.queue = queue
            self.running = False
            Thread.__init__(self)
            
        def run(self):
            es.dbgmsg(1, "Urllib2DownloadManager: Running Thread")
            self.running = True
            while self.running:
                request = self.queue.get()
                es.dbgmsg(1, "Urllib2DownloadManager: handling request: %s"
                             % request.path)
                success = False
                try:
                    u = urllib2.urlopen(request.path,
                                        request.querystring,
                                        30)
                    value   = u.read()
                    success = True
                except urllib2.URLError, e:
                    value = e.message
                response = Response(value, success, request.get_duration(),
                                    request)
                request.callback(response)
                
    def __init__(self):
        self.queue = Queue()
        self.thread = self.DownloaderThread(self.queue)
        
    def download(self, url, data={}, callback=lambda x,y: None):
        request = Request(url, data, callback)
        self.queue.put(request)
        if not self.thread.running:
            self.thread.start()
        
    def cleanup(self):
        self.queue = Queue()
        self.thread.running = False


class WgetDownloadManager(object):
    """
    Gamethreaded wget downloader.
    """
    tpl = 'wget -q --output-document='
    tpl += str(TEMP_DL_FILE)
    tpl += ' --timeout=30 --post-data=%s %s'
    gtname = 'xawebsyncgt'
    
    def __init__(self):
        self.queue = Queue()
        self.nextcallback = None
        self.request = None
        
    def download(self, url, data={}, callback=lambda x,y: None):
        es.dbgmsg(1, "WgetDownloadManager: Scheduling %s" % url)
        request = Request(url, data, callback)
        if self.request is None:
            es.dbgmsg(1, "WgetDownloadManager: Empty queue, starting download")
            self._start_download(request)
        else:
            self.queue.put(request)
        return request
            
    def _start_download(self, request):
        if os.path.exists(TEMP_DL_FILE):
            os.remove(TEMP_DL_FILE)
        os.system(self.tpl % (request.querystring, request.path))
        self.request = request
        self.timeout = 31
        gamethread.delayedname(1, self.gtname, self._check)
        es.dbgmsg(1, "WgetDownloadManager: Download started: %s" % request.path)
        
    def _check(self):
        es.dbgmsg(1,
            "WgetDownloadManager: Checking wget download, timeleft %s"
            % self.timeout
        )
        if os.path.exists(TEMP_DL_FILE):
            f = open(TEMP_DL_FILE, 'rb')
            data = f.read()
            f.close()
            response = Response(data,
                                True,
                                self.request.get_duration(),
                                self.request)
            self.request.callback(response)
            if self.queue:
                return self._start_download(self.queue.get())
            else:
                self.request = None
        elif not self.timeout:
            response = Response('Timeout',
                                False,
                                self.request.get_duration(),
                                self.request)
            self.request.callback(response)
            if self.queue:
                return self._start_download(self.queue.get())
            else:
                self.request = None
        else:
            self.timeout -= 1
            gamethread.delayedname(1, self.gtname, self._check)
            
    def cleanup(self):
        if self.request is not None:
            gamethread.cancelDelayed(self.gtname)


def get_default_downloader():
    """
    On Linux it returns the wget_downloader if wget is installed, otherwise it
    returns the urllib2_downloader
    """
    if os.name == 'posix':
        if os.popen('wget -V').read().lower().startswith('gnu wget'):
            return WgetDownloadManager()
    return Urllib2DownloadManager()
downloader = get_default_downloader()