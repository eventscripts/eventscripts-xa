from django.conf import settings

DEFAULTS = {
    'WIKI_SS_PATH': None,
    'WIKI_SS_URL_PREFIX': 'ss',
    'WIKI_GFX_PATH': None,
    'WIKI_GFX_URL_PREFIX': 'js',
    'WIKI_JS_PATH': None,
    'WIKI_JS_URL_PREFIX': 'gfx',
}

def get(key, default=None):
    """
    Get the configuration value for a given key
    """
    if hasattr(settings, key):
        return getattr(settings, key)
    return DEFAULTS.get(key, default)
