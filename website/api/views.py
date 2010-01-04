from django.template.loader import render_to_string
from django.template import RequestContext
from xa.utils import response
from xa.groupauth.models import Config

@response
def version(request):
    return '1.0.0.500', 'text/plain'

@response
def gauth(request, configid):
    cfg = Config.objects.get_or_none(id=configid)
    if not cfg:
        return 'Config Not Found', 'text/plain'
    context = RequestContext(request, {
        'config': cfg,
    })
    return render_to_string('groupauth/config.txt', context), 'text/plain'
