# This file is part of tofbot, a friendly IRC bot.
# You may redistribute it under the Simplified BSD License.
# If we meet some day, and you think this stuff is worth it,
# you can buy us a beer in return.
#
# Copyright (c) 2012 Etienne Millon <etienne.millon@gmail.com>

from urllib.parse import urlparse

from bs4 import BeautifulSoup
import httpx

from tofbot.toflib import Plugin

SHORTEN_NETLOCS = ["t.co", "tinyurl.com", "bit.ly", "www.bit.ly"]

YOUTUBE_NETLOCS = ["youtube.com", "www.youtube.com", "youtu.be"]


def is_mini(url):
    return url.netloc in SHORTEN_NETLOCS


def is_youtube(url):
    return url.netloc in YOUTUBE_NETLOCS


async def url_expand(url, cookies):
    async with httpx.AsyncClient() as client:
        r = await client.get(url, cookies=cookies)
        return r.headers.get("Location")

async def oh_yes_cookies(url, cookies):
    """
    Oh sure that bot accepts the cookies from your 23521 parters.

    This might update the ``cookies`` dict.
    """
    async with httpx.AsyncClient() as client:
        r = await client.head(url)
        r.raise_for_status()
        if "CONSENT" in r.cookies:
            if "PENDING" in r.cookies["CONSENT"]:
                cookies["CONSENT"] = "YES+cb.20210328-17-p0.en+FX+100"


async def get_title(url, cookies):
    async with httpx.AsyncClient() as client:
        r = await client.get(url, cookies=cookies)
        r.raise_for_status()
        c = r.content
        s = BeautifulSoup(c, "html.parser")
        t = s.html.head.title.string
        return "".join(t.split("\n")).strip()


class PluginExpand(Plugin):
    async def on_url(self, url):
        cookies = dict()
        u = urlparse(url)

        try:
            # prepare cookies
            if is_youtube(u):
                await oh_yes_cookies(url, cookies)

            if is_mini(u):
                exp = await url_expand(url, cookies)
                if exp != url:
                    await self.say(exp)

            if is_youtube(u):
                t = await get_title(url, cookies)
                await self.say(t)
        except (httpx.HTTPError, AttributeError):
            pass
