from django.contrib.syndication.feeds import Feed
from django.utils.feedgenerator import Atom1Feed
from models import News, Release

class NewsFeedRSS(Feed):
    title = 'eXtensible Admin news'
    link  = '/news/'
    description = 'News about the eXtensible Admin project.'

    description_template = '/feeds/news.htm'

    def items(self):
        return News.objects.order_by('-postdate')[:10]


class NewsFeedAtom(NewsFeedRSS):
    feed_type = Atom1Feed
    subtitle = NewsFeedRSS.description

class ReleasesFeedRSS(Feed):
    title = 'eExtensible Admin releases'
    link  = '/releases/'
    description = 'Releases of the eXtensible Admin project.'

    description_template = 'feeds/release.htm'

    def items(self):
        return Release.objects.order_by('-releasedate')[:10]


class ReleasesFeedAtom(ReleasesFeedRSS):
    feed_type = Atom1Feed
    subtitle = ReleasesFeedRSS.description
