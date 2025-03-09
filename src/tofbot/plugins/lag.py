# This file is part of tofbot, a friendly IRC bot.
# You may redistribute it under the Simplified BSD License.
# If we meet some day, and you think this stuff is worth it,
# you can buy us a beer in return.
#
# Copyright (c) 2015 Christophe-Marie Duquesne <chmd@chmd.fr>

"See PluginLag"

import datetime
import time
import collections

from tofbot.toflib import Plugin, cmd

Mention = collections.namedtuple("Mention", "timestamp author msg pending")
datetime_now = datetime.datetime.now


def timeformat(t):
    "return a formatted time element without microseconds"
    return str(t).split(".")[0]


class PluginLag(Plugin):
    "Lag: time between a mention and the answer"

    def __init__(self, bot):
        # A dictionary of nick -> dict
        # Values are like this:
        #  {
        #      "mentions": list(Mention)
        #      "previous_lag": timedelta
        #      "last_active": timestamp
        #  }
        super(PluginLag, self).__init__(bot)
        self.data = {}

    def garbage_collect(self):
        "Limit memory usage"
        # don't watch more than 20 nicks
        while len(self.data) > 20:
            least_active_nick = max(
                self.data.keys(), key=lambda x: self.data[x]["last_active"]
            )
            del self.data[least_active_nick]
        # don' keep more than 5 mentions per nick
        for nick in self.data:
            while len(self.data[nick]["mentions"]) > 10:
                del self.data[nick]["mentions"][0]

    def set_active(self, nick):
        "Update the last moment the nick was active"
        # If the nick did not exist, add it
        if nick not in self.data:
            self.data[nick] = {"mentions": [], "previous_lag": None}
        self.data[nick]["last_active"] = datetime_now()
        self.garbage_collect()

    async def on_join(self, chan, nick):
        "When a nick joins, mark it as active"
        self.set_active(nick)

    def add_mention(self, msg_text, author, to, pending=True):
        "Add a mention to the nick"
        self.data[to]["mentions"].append(
            Mention(
                timestamp=datetime_now(), author=author, msg=msg_text, pending=pending
            )
        )
        self.garbage_collect()

    def lag(self, nick):
        "Returns the time between now and the oldest pending mention"
        now = datetime_now()
        if nick in self.data:
            for m in self.data[nick]["mentions"]:
                if m.pending:
                    return now - m.timestamp
        return None

    async def handle_msg(self, msg_text, _chan, me):
        "Process mentions and update previous lag"
        self.set_active(me)

        words = set(msg_text.replace(":", " ").replace(",", " ").strip().split(" "))

        # skip commands
        if msg_text.strip().startswith("!"):
            return

        # did I mention anybody, except myself?
        for nick in self.data.keys():
            if nick != me and nick in words:
                self.add_mention(msg_text, me, nick)

        # update my lag
        lag = self.lag(me)
        if lag is not None:
            self.data[me]["previous_lag"] = lag

        # my mentions are no longer pending since I just answered
        mentions = self.data[me]["mentions"]
        for i in range(len(mentions)):
            mentions[i] = mentions[i]._replace(pending=False)

    @cmd(1)
    async def cmd_lag(self, chan, args, sender_nick):
        "Report the lag of the given nick"
        who = args[0]
        if who not in self.data:
            await self.say(f"Pas d'infos sur {who}.")
            return

        lag = self.lag(who)
        if lag is not None:
            await self.say(f"Le {who}-lag du moment est de {timeformat(lag)}.")
        else:
            previous_lag = self.data[who]["previous_lag"]
            if previous_lag is not None:
                await self.say(
                    f"Pas de lag pour {who} (lag précédent: {timeformat(previous_lag)})."
                )
            else:
                await self.say(f"Pas de lag pour {who}.")

    @cmd(0, 1)
    async def cmd_mentions(self, chan, args, sender_nick):
        "Report the recent mentions of the given nick"
        who = sender_nick
        if len(args) >= 1:
            who = args[0]

        if who not in self.data:
            await self.private(sender_nick, f"Pas d'infos sur {who}.")
            return

        mentions = self.data[who]["mentions"]
        if len(mentions) > 0:
            await self.private(sender_nick, f"Dernières mentions de {who}:")
            for m in mentions:
                status = "✗" if m.pending else "✓"
                time.sleep(0.5)
                await self.private(
                    sender_nick,
                    "[%s] %s <%s> %s"
                    % (status, timeformat(m.timestamp), m.author, m.msg),
                )
        else:
            await self.private(sender_nick, f"Pas de mentions pour {who}.")
