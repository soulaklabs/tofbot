# This file is part of tofbot, a friendly IRC bot.
# You may redistribute it under the Simplified BSD License.
# If we meet some day, and you think this stuff is worth it,
# you can buy us a beer in return.
#
# Copyright (c) 2011 Etienne Millon <etienne.millon@gmail.com>

"See PluginSed"

import re

from tofbot.toflib import Plugin

class PluginSed(Plugin):
    "That's what she sed"

    def __init__(self, bot):
        Plugin.__init__(self, bot)
        self.msg = None

    async def handle_msg(self, msg_text, chan, nick):
        r = "s/(.*?)/(.*?)/?$"
        m = re.match(r, msg_text)

        if m is not None and self.msg is not None:
            regexp = m.group(1)
            try:
                regexp = re.compile(regexp)
            except re.error:
                pass
            to = m.group(2)
            msg_who = self.msg[0]
            msg_what = self.msg[1]
            try:
                new_msg = re.sub(regexp, to, msg_what)
                if new_msg != msg_what:
                    await self.say("<%s> : %s" % (msg_who, new_msg))
                    self.msg = (nick, new_msg)
            except (TypeError, ValueError):
                pass
        else:
            self.msg = (nick, msg_text)
