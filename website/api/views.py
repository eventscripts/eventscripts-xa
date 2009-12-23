from xa.utils import response

@response
def version(request):
    return '1.0.0.500', 'text/plain'