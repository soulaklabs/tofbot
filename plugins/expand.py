# -*- coding: utf-8 -*-
#
# This file is part of tofbot, a friendly IRC bot.
# You may redistribute it under the Simplified BSD License.
# If we meet some day, and you think this stuff is worth it,
# you can buy us a beer in return.
#
# Copyright (c) 2012 Etienne Millon <etienne.millon@gmail.com>

from bs4 import BeautifulSoup
import requests
import re
from urllib.parse import urlparse

from toflib import Plugin

SHORTEN_NETLOCS = ["t.co", "tinyurl.com", "bit.ly", "www.bit.ly"]

YOUTUBE_NETLOCS = ["youtube.com", "www.youtube.com", "youtu.be"]


def is_mini(url):
    return url.netloc in SHORTEN_NETLOCS


def is_youtube(url):
    return url.netloc in YOUTUBE_NETLOCS


def urlExpand(url, cookies=dict()):
    r = requests.get(url, cookies=cookies)
    return r.url


def getTitle(url, cookies=dict()):
    r = requests.get(url, cookies=cookies)
    c = r.content
    s = BeautifulSoup(c, "html.parser")
    t = s.html.head.title.string
    return ''.join(t.split("\n")).strip()


class PluginExpand(Plugin):

    def on_url(self, url):
        cookies = dict()
        u = urlparse(url)

        # prepare cookies
        if is_youtube(u):
            consent = None
            r = requests.head(url)
            if 'CONSENT' in r.cookies:
                consent = r.cookies['CONSENT']
                if 'PENDING' in consent:
                    cookies['CONSENT'] = 'YES+cb.20210328-17-p0.en+FX+100'

        if is_mini(u):
            try:
                exp = urlExpand(url, cookies)
                self.say(exp)
            except (requests.exceptions.RequestException, requests):
                pass

        if is_youtube(u):
            try:
                t = getTitle(url, cookies)
                self.say(t)
            except (requests.exceptions.RequestException, AttributeError):
                pass
