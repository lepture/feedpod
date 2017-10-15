# coding: utf-8

import datetime
from .parser import Parser

INDEX_URL = 'http://www3.nhk.or.jp/news/easy/'

SITE = dict(
    title='News Easy',
    link=INDEX_URL,
    language='ja',
    description=(
        u'NEWS WEB EASYは、小学生・中学生の皆さんや、'
        u'日本に住んでいる外国人のみなさんに、わかりやすいことば'
        u'でニュースを伝えるウェブサイトです。'
    ),
    subtitle='NHK NEWS WEB EASY',
    author='NHK',
    image='https://feeds.doocer.com/images/newseasy.jpg',
    email='',
    explicit='no',
    category='Education',
)


class NewsEasyParser(Parser):
    NAME = 'newseasy'
    ENCODING = 'utf-8'
    INDEX_API = 'http://www3.nhk.or.jp/news/easy/top-list.json'

    def fetch_index(self):
        resp = self.session.get(self.INDEX_API)
        items = []
        for d in resp.json():
            news_id = d['news_id']
            url = '{}{}/{}.html'.format(INDEX_URL, news_id, news_id)
            item = self.fetch_item(url)
            self._extend_item(item, d)
            items.append(item)
        return dict(podcast=SITE, items=items)

    def parse_item(self, resp):
        dom = resp.dom
        audio_url = resp.url.replace('.html', '.mp3')
        item = dict(
            author='NHK',
            explicit='no',
            subtitle='',
            link=resp.url,
            audio_url=audio_url,
        )

        el = dom.find('div', id='newsarticle')

        for rt in el.find_all('rt'):
            rt.extract()

        for ruby in el.find_all('ruby'):
            ruby.unwrap()

        for a in el.find_all('a'):
            a.unwrap()

        content = el.decode_contents(formatter="html")
        item['content'] = content

        info = self.fetch_audio(audio_url)
        item['audio_size'] = info['size']
        item['duration'] = info['duration']
        return item

    def _extend_item(self, item, d):
        item['title'] = d['title']
        pubdate = d['news_prearranged_time']
        date = datetime.datetime.strptime(pubdate, '%Y-%m-%d %H:%M:%S')
        item['pubdate'] = date.strftime('%a, %d %b %Y %H:%M:%S +0900')
        return item
