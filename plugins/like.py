# -*- coding: utf-8 -*-
#
# This file is part of tofbot, a friendly IRC bot.
# You may redistribute it under the Simplified BSD License.
# If we meet some day, and you think this stuff is worth it,
# you can buy us a beer in return.
#
# Copyright (c) 2012 Etienne Millon <etienne.millon@gmail.com>

from collections import deque
from toflib import cmd, Plugin


class PluginLike(Plugin):

    def __init__(self, bot):
        Plugin.__init__(self, bot)
        self.previous_speaker = None
        self.scores = {}

    def load(self, data):
        for nick in self.bot.names:
            if nick not in self.scores:
                self.scores[nick] = [0, 0]

    def on_join(self, chan, nick):
        if nick not in self.scores:
            self.scores[nick] = [0, 0]

    def handle_msg(self, msg_text, chan, nick):
        if not msg_text.strip().startswith("!"):
            self.previous_speaker = nick
        if nick not in self.scores:
            self.scores[nick] = [0, 0]

    def give(self, n, nick):
        if nick not in self.scores:
            return
        self.scores[nick][0] += n
        self.scores[nick][1] += 1
        self.say(nick + ": " + "★" * n + "☆" * (5-n))

    def avg_stars(self, nick):
        if nick not in self.scores or self.scores[nick][1] == 0:
            return None
        return float(self.scores[nick][0])/self.scores[nick][1]

    @cmd(2)
    def cmd_starz(self, _chan, args, sender):
        "Give starz to someone"
        try:
            n = min(max(int(args[0]), 0), 5)
        except ValueError:
            return
        nick = args[1]
        if sender != nick:
            self.give(n, nick)

    @cmd(0)
    def cmd_like(self, _chan, _args, sender):
        "Alias for '!starz 4 <previous speaker>'"
        if sender != self.previous_speaker:
            if self.previous_speaker is not None:
                self.give(4, self.previous_speaker)

    @cmd(1)
    def cmd_score(self, _chan, args):
        "Give someone's starz average"
        nick = args[0]
        avg = self.avg_stars(nick)
        if avg is None:
            self.say("%s n'a pas de starz." % nick)
        else:
            self.say("%s: %.1f starz de moyenne." % (nick, avg))

    @cmd(0)
    def cmd_ggg(self, _chan, args):
        "Tell who is the current Good Guy Greg"
        if not self.scores:
            return
        nick = max(self.scores, key=self.avg_stars)
        avg = self.avg_stars(nick)
        if avg is not None:
            self.say("%s est le Good Guy Greg du moment avec %.1f starz "
                     "de moyenne" % (nick, avg))
