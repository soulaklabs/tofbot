# This file is part of tofbot, a friendly IRC bot.
# You may redistribute it under the Simplified BSD License.
# If we meet some day, and you think this stuff is worth it,
# you can buy us a beer in return.
#
# Copyright (c) 2015 Etienne Millon <me@emillon.org>

from toflib import Plugin
from operator import itemgetter
from datetime import datetime, timedelta
import re

datetime_now = datetime.now


class Game(object):

    def __init__(self, nick, join_time):
        self.nick = nick
        self.join_time = join_time
        self._bets = {}

    def add_bet(self, nick, expected_leave_time):
        if nick not in self._bets:
            self._bets[nick] = expected_leave_time

    def end(self, leave_time):
        def ok(dt):
            return dt <= leave_time
        ok_bets = [(nick,dt) for nick,dt in self._bets.items() if ok(dt)]
        if ok_bets:
            winner_bet = max(ok_bets, key=itemgetter(1))
            return winner_bet[0]
        else:
            return


def next_with_minute_equal_to(minute):
    now = datetime_now()
    dt = now.replace(minute=minute)
    if not (dt > now):
        dt = dt.replace(hour=dt.hour + 1)
    return dt


class PluginRisoli(Plugin):

    def __init__(self, bot):
        super(PluginRisoli, self).__init__(bot)
        self._game = None
        self._next_game = None

    def on_join(self, chan, nick):
        self._next_game = Game(nick, datetime_now())

    def _register_leave(self, nick):
        if self._game and self._game.nick == nick:
            leave_time = datetime_now()
            winner = self._game.end(leave_time)
            if winner is not None:
                self.say('%s gagne un Point Internet' % winner)
            self._game = None

    def on_leave(self, chan, nick):
        self._register_leave(nick)

    def on_quit(self, nick):
        self._register_leave(nick)

    def handle_msg(self, msg_text, chan, nick):
        m = re.match('%s: (\\d+)' % re.escape(self.bot.nick), msg_text)
        if not m:
            return
        if not self._game:
            self._game = self._next_game
        if self._game:
            bet = int(m.group(1))
            try:
                expected_leave_time = next_with_minute_equal_to(bet)
            except ValueError:
                return
            if expected_leave_time is not None:
                self._game.add_bet(nick, expected_leave_time)
