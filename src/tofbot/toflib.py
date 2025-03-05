# This file is part of tofbot, a friendly IRC bot.
# You may redistribute it under the Simplified BSD License.
# If we meet some day, and you think this stuff is worth it,
# you can buy us a beer in return.
#
# Copyright (c) 2011 Etienne Millon <etienne.millon@gmail.com>
#                    Martin Kirchgessner <martin.kirch@gmail.com>
#                    Nicolas Dumazet <nicdumz.commits@gmail.com>
#                    Quentin Sabah <quentin.sabah@gmail.com>
import random
import re
import time
from datetime import datetime, timedelta

# those commands directly trigger cmd_* actions
_simple_dispatch = set()


def cmd(nargs_min, nargs_max=None):
    if nargs_max is None:
        nargs_max = nargs_min

    def deco(func):
        name = func.__name__[4:]
        _simple_dispatch.add(name)

        async def f(bot, chan, args, sender_nick="nobody"):
            if nargs_min <= len(args) <= nargs_max:
                return await func(bot, chan, args, sender_nick)

        f.__doc__ = func.__doc__
        return f

    return deco


def distance(string1, string2):
    """
    Levenshtein distance
    http://en.wikibooks.org/wiki/Algorithm_implementation/Strings/Levenshtein_distance#Python
    """
    string1 = " " + string1
    string2 = " " + string2
    dists = {}
    len1 = len(string1)
    len2 = len(string2)
    for i in range(len1):
        dists[i, 0] = i
    for j in range(len2):
        dists[0, j] = j
    for j in range(1, len2):
        for i in range(1, len1):
            if string1[i] == string2[j]:
                dists[i, j] = dists[i - 1, j - 1]
            else:
                dists[i, j] = min(
                    dists[i - 1, j] + 1, dists[i, j - 1] + 1, dists[i - 1, j - 1] + 1
                )
    return dists[len1 - 1, len2 - 1]


class RiddleTeller(object):
    """
    A gentleman (and a scholar) who likes to entertain its audience.
    """

    def __init__(self, riddle, channel, writeback, max_dist):
        self.riddle, self.answer = riddle
        self.channel = channel
        self.writeback = writeback
        self.remaining_msgs = 3
        self.max_dist = max_dist

    async def start(self):
        await self.writeback(self.riddle)

    async def wait_answer(self, chan, msg):
        """
        Called at each try.
        Returns True iff the riddle is over.
        """
        if chan != self.channel:
            return False
        if distance(msg.lower(), self.answer.lower()) < self.max_dist:
            await self.writeback("10 points pour Griffondor.")
            return True
        self.remaining_msgs -= 1
        if self.remaining_msgs == 0:
            await self.writeback(self.answer)
            return True
        return False


class InnocentHand(object):
    """
    A cute 6 years old girl, picking a random object
    from a given pool of candidates
    """

    def __init__(self, pool: list):
        """
        pool: list of candidates
        """
        self.pool = pool

    def __call__(self, index=None):
        if index:
            return self.pool[index % len(self.pool)]
        return random.choice(self.pool)


class Plugin(object):
    def __init__(self, bot):
        self.bot = bot

    async def say(self, msg):
        to = self.bot.channels[0]
        await self.bot.msg(to, msg)

    async def private(self, to, msg):
        await self.bot.msg(to, msg)

    def tofade_time(self, has_context=True):
        "Is it a good time for a tofade"
        threshold = self.bot.autoTofadeThreshold
        if has_context:
            threshold = int(threshold * 0.9)
        return (
            time.time() - self.bot.lastTGtofbot >= self.bot.TGtime * 10 * 60
            and random.randint(0, 100) > threshold
        )

    def load(self, data):
        "Called after plugin initialization to set its internal state"
        pass

    def save(self):
        "Called periodically to serialize data to a file"
        return {}

    async def on_url(self, url):
        pass

    async def on_join(self, chan, nick):
        pass

    async def on_leave(self, chan, nick):
        pass

    async def on_quit(self, nick):
        pass

    async def handle_msg(self, text, chan, nick):
        pass

    async def on_kick(self, chan, reason):
        pass


class CronEvent:
    def __init__(self, plugin):
        self.lastTick = datetime.min
        self.period = timedelta(minutes=10)
        self.plugin = plugin

    def fire(self):
        pass


class Cron:
    def __init__(self):
        self.events = []

    def tick(self):
        now = datetime.now()
        for ev in self.events:
            if now > ev.lastTick + ev.period:
                ev.fire()
                ev.lastTick = now

    def schedule(self, ev):
        self.events.append(ev)


# http://daringfireball.net/2010/07/improved_regex_for_matching_urls
# Public Domain
RE_URL = re.compile(
    r"""(?xi)
    \b
    (                           # Capture 1: entire matched URL
      (?:
        https?:                     # URL protocol and colon
        (?:
          /{1,3}                        # 1-3 slashes
          |                             #   or
          [a-z0-9%]                     # Single letter or digit or '%'
                                        # (Trying not to match e.g.
                                        # "URI::Escape")
        )
        |                           #   or
        www\d{0,3}[.]               # "www.", "www1.", "www2." … "www999."
        |                           #   or
        [a-z0-9.\-]+[.][a-z]{2,4}/  # looks like domain name followed by
                                    # a slash
      )
      (?:                           # One or more:
        [^\s()<>]+                      # Run of non-space, non-()<>
        |                               #   or
        \(([^\s()<>]+|(\([^\s()<>]+\)))*\)  # balanced parens, up to 2 levels
      )+
      (?:                           # End with:
        \(([^\s()<>]+|(\([^\s()<>]+\)))*\)  # balanced parens, up to 2 levels
        |                                   #   or
        [^\s`!()\[\]{};:'".,<>?«»“”‘’]        # not a space or one of these
                                              # punct chars
      )
    )
    """
)


def urls_in(text):
    return [m[0] for m in RE_URL.findall(text)]
