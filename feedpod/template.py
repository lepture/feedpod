import datetime


def gen_feed(podcast, items):
    xml = (
        '<rss xmlns:content="http://purl.org/rss/1.0/modules/content/" '
        'xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd" '
        'xmlns:atom="http://www.w3.org/2005/Atom" version="2.0">'
        '<channel>'
    )
    xml += u''.join(_gen_channel(podcast))
    for item in items:
        xml += u''.join(_gen_item(podcast, item))
    xml += '</channel></rss>'
    return xml


def _gen_channel(podcast):
    now = datetime.datetime.utcnow()
    yield '<generator>Feedpod (https://github.com/lepture/feedpod)</generator>'

    for k in ['title', 'link', 'description', 'language']:
        yield u'<{}>{}</{}>'.format(k, podcast[k], k)

    yield '<pubDate>{}</pubDate>'.format(_rssdatetime(now))

    for k in ['subtitle', 'author', 'image', 'explicit']:
        yield u'<itunes:{}>{}</itunes:{}>'.format(k, podcast[k], k)

    yield u'<itunes:summary>{}</itunes:summary>'.format(podcast['description'])
    yield '<itunes:owner>'
    yield u'<itunes:name>{}</itunes:name>'.format(podcast['author'])
    yield u'<itunes:email>{}</itunes:email>'.format(podcast['email'])
    yield '</itunes:owner>'
    yield u'<itunes:category text="{}"/>'.format(podcast['category'])


def _gen_item(podcast, item):
    yield '<item>'
    yield '<enclosure url="{}" length="{}" type="audio/mpeg"/>'.format(
        item['audio_url'], item['audio_size']
    )
    yield u'<title>{}</title>'.format(item['title'])
    yield u'<guid>{}</guid>'.format(item['link'])
    yield u'<link>{}</link>'.format(item['link'])

    for k in ['author', 'subtitle', 'duration', 'explicit']:
        yield u'<itunes:{}>{}</itunes:{}>'.format(k, item[k], k)

    yield '<itunes:image href="{}"/>'.format(podcast['image'])

    html = u'<![CDATA[ {} ]]>'.format(item['content'])
    yield u'<itunes:summary>{}</itunes:summary>'.format(html)
    yield u'<content:encoded>{}</content:encoded>'.format(html)
    yield '<pubDate>{}</pubDate>'.format(item['pubdate'])
    yield '</item>'


def _rssdatetime(date):
    return date.strftime('%a, %d %b %Y %H:%M:%S +0000')
