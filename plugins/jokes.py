# -*- coding: utf-8 -*-
#
# This file is part of tofbot, a friendly IRC bot.
# You may redistribute it under the Simplified BSD License.
# If we meet some day, and you think this stuff is worth it,
# you can buy us a beer in return.
#
# Copyright (c) 2011 Etienne Millon <etienne.millon@gmail.com>
#                    Martin Kirchgessner <martin.kirch@gmail.com>
#                    Nicolas Dumazet <nicdumz.commits@gmail.com>
import time
from datetime import timedelta

from tofdata.chucknorris import chuckNorrisFacts
from tofdata.riddles import riddles
from tofdata.fortunes import fortunes
from tofdata.contrepeteries import contrepeteries
from toflib import cmd, InnocentHand, RiddleTeller, Plugin, CronEvent


class PluginJokes(Plugin):

    def __init__(self, bot):
        Plugin.__init__(self, bot)
        self._chuck = InnocentHand(chuckNorrisFacts)
        self._riddles = InnocentHand(riddles)
        self._fortunes = InnocentHand(fortunes)
        self._contrepeteries = InnocentHand(contrepeteries)
        bot._mutable_attributes["autoTofadeThreshold"] = int
        bot._mutable_attributes["riddleMaxDist"] = int

    @cmd(0)
    def cmd_fortune(self, chan, args, sender_nick):
        "Tell great philosophy"
        self.say(self._fortunes())

    @cmd(0)
    def cmd_chuck(self, chan, args, sender_nick):
        "Tell a Chuck Norris fact"
        self.say(self._chuck())

    @cmd(0)
    def cmd_contrepeterie(self, chan, args, sender_nick):
        "Tell a contrepeterie"
        self.say(self._contrepeteries())

    @cmd(0)
    def cmd_devinette(self, chan, args, sender_nick):
        "Riddle teller"
        if not self.active_riddle():
            self.devinette = self.random_riddle(chan)

    def handle_msg(self, msg_text, chan, nick):
        stripped = msg_text.strip().lower()
        if stripped.find(self.bot.nick, 1) >= 0 and self.tofade_time():
            self.say(nick + ": Ouais, c'est moi !")
        if stripped.find("toughbot", 1) >= 0 and self.tofade_time():
            self.say(nick + ": Je suis balèze ! BALÈZE !")
        if self.active_riddle():
            itsOver = self.devinette.wait_answer(chan, msg_text)
            if itsOver:
                self.devinette = None

    def active_riddle(self):
        return (hasattr(self, 'devinette') and self.devinette is not None)

    def random_riddle(self, chan):
        riddle = self._riddles()
        r = RiddleTeller(riddle, chan, self.say,
                         self.bot.riddleMaxDist)
        return r

    def on_kick(self, chan, reason):
        bot = self.bot
        if reason == bot.nick:
            respawn_msg = 'respawn, LOL'
        else:
            respawn_msg = 'comment ça, %s ?' % reason
        bot.msg(chan, respawn_msg)
