# -*- coding: utf-8 -*-

from common import TofbotTestCase, set_clock, bot_kick
from mock import patch


class TestLag(TofbotTestCase):

    def test_unknown_nick(self):
        self.assertOutput('!lag kevin', "Pas d'infos sur kevin.")
        self.assertOutput('!mentions kevin', "Pas d'infos sur kevin.")

    def test_no_lag(self):
        self.bot.send('hello!', origin='kevin')
        self.assertOutput('!lag kevin', "Pas de lag pour kevin.")
