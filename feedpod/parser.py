import os
import time
import json
import hashlib
import requests
from bs4 import BeautifulSoup
from mutagen.mp3 import MP3
from .template import gen_feed

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


class Parser(object):
    HTTP_DELAY = 1
    ENCODING = None
    USER_AGENT = 'Mozilla/5.0 feedpod/1.0'

    def __init__(self):
        self.cache_dir = os.path.join(ROOT, 'cache', self.NAME)
        if not os.path.isdir(self.cache_dir):
            os.makedirs(self.cache_dir)

        self.build_dir = os.path.join(ROOT, 'build')
        if not os.path.isdir(self.build_dir):
            os.makedirs(self.build_dir)

        self._req_count = 0
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': self.USER_AGENT})

    def build(self):
        info = self.fetch_index()
        xml = gen_feed(**info)
        file_path = os.path.join(self.build_dir, self.NAME + '.xml')
        with open(file_path, 'wb') as f:
            f.write(xml.encode('utf-8'))

    def request(self, url, params=None, headers=None):
        if self._req_count:
            time.sleep(self.HTTP_DELAY)
        self._req_count += 1
        resp = self.session.get(url, params=params, headers=headers)
        if resp.status_code == 200:
            if self.ENCODING:
                resp.encoding = self.ENCODING
            resp.dom = BeautifulSoup(resp.text, 'html.parser')
            return resp
        print('GET {} - {}'.format(resp.url, resp.status_code))

    def fetch_item(self, url):
        hasher = hashlib.sha1(url)
        key = hasher.hexdigest()
        file_path = os.path.join(self.cache_dir, key + '.json')
        if os.path.isfile(file_path):
            with open(file_path, 'rb') as f:
                return json.load(f)

        resp = self.request(url)
        data = self.parse_item(resp)

        with open(file_path, 'wb') as f:
            json.dump(data, f)
        return data

    def fetch_audio(self, url):
        hasher = hashlib.sha1(url)
        key = hasher.hexdigest()
        file_path = os.path.join(self.cache_dir, key + '.mp3')

        resp = self.session.get(url, stream=True)
        size = resp.headers.get('Content-Length')

        chunk_size = 1024 * 1024
        with open(file_path, 'wb') as f:
            for chunk in resp.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)

        resp.close()

        audio = MP3(file_path)
        duration = int(audio.info.length)
        # TODO: delete cache
        return dict(duration=duration, size=size)
