from models import News, Release
from xa.utils import render_to

@render_to
def home(request):
    return 'home/home.htm', {'news': News.objects.all()[:5]}

@render_to
def download(request, version=None):
    if version is None:
        release = Release.objects.all().latest()
    else:
        release = Release.objects.get_or_404(version=version)
    return 'home/download.htm', {'release': release}

@render_to
def releases(request):
    return 'home/releases.htm', {'releases': Release.objects.all()}