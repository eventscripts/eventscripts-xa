from django.contrib.syndication.feeds import Feed
from django.utils.feedgenerator import Atom1Feed
from models import News

class NewsFeedRSS(Feed):
    title = 'eXtensible Admin news'
    link  = '/news/'
    description = 'News about the eXtensible Admin project.'

    description_template = '/home/feeditem.htm'

    def items(self):
        return News.objects.order_by('-postdate')[:10]


class NewsFeedAtom(NewsFeedRSS):
    feed_type = Atom1Feed
    subtitle = NewsFeedRSS.description
