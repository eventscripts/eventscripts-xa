"""
XA Web Sync:
    Allows you to sync your group auth files with those on the xa website.
"""
import os
import es
import popuplib

from xa import xa

from downloaders import downloader

URL_TEMPLATE    = "http://dev.xa.ojii.ch/api/gauth/%(config_id)s/"
GAMEDIR         = str(es.ServerVar('eventscripts_gamedir'))

xawebsync   = xa.register('xawebsync')

config_id = xawebsync.setting.createVariable(
    "websync_config_id",
    -1,
    "The ID of your configuration file on the website."
)

config_name = xawebsync.setting.createVariable(
    "websync_config_name",
    "",
    "The config name of your group auth file."
)

def load():
    """
    Executed when the module loads. Register server command and ensure that
    everything is registered
    """
    xawebsync.addCommand(
        'xa_websync',
        websync_handle,
        "xa_websync",
        "UNRESTRICTED",
        "Web Sync",
        True
    ).register(('server', 'console'))
    
def websync_handle():
    """
    Synchronize from the web. This just overwrites the local copy of the file!
    """
    # Check config values
    if int(config_id) < 1:
        return es.dbgmsg(0, "Invalid config id")
    if not str(config_name):
        return es.dbgmsg(0, "Invalid config name")
    es.dbgmsg(0, "WebSync: Starting download...")
    request = downloader.download(URL_TEMPLATE % {'config_id': config_id},
                                  callback=download_postprocess)
    
def download_postprocess(response):
    if not response.success:
        es.dbgmsg(0, "WebSync failed: %s" % response.data)
    else:
        es.dbgmsg(0, "WebSync successful in %0.3f seconds" % response.duration)
        f = open(os.path.join(GAMEDIR, "cfg", str(config_name)), 'wb')
        f.write(response.data)
        f.close()