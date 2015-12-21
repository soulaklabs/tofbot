# -*- coding: utf-8 -*-

from common import TofbotTestCase, set_clock, bot_kick
from mock import patch


class TestLol(TofbotTestCase):

    def test_lol_kevin(self):
        self.assertOutput('!kevin', 'pas de Kevin')
        for msg in ['lol', 'lolerie']:
            self.bot.send(msg, origin='michel')
        self.assertOutput('!kevin',
                          'michel est le Kevin du moment avec 2 lolades')
        for msg in ['lulz', 'LOL', '10L']:
            self.bot.send(msg, origin='alfred')
        self.assertOutput('!kevin',
                          'alfred est le Kevin du moment avec 3 lolades')

    @patch('plugins.lolrate.datetime_now')
    def test_lol_rate(self, now_mock):

        self.bot.send('!set lolRateDepth 2')
        self.assertOutput('!get lolRateDepth', 'lolRateDepth = 2')

        set_clock(now_mock, 12)
        self.bot.send('lol')
        self.bot.send('lol')
        expected = '16 Feb 12h-13h : 2 lolz'
        self.assertOutput('!lulz', expected)
        # check that the command itself does not increment
        self.assertOutput('!lulz', expected)

        set_clock(now_mock, 13)
        self.bot.send('lol')
        self.assertOutput('!lulz', ['16 Feb 13h-14h : 1 lolz',
                                    expected,
                                    ])

        set_clock(now_mock, 14)
        self.bot.send('lol')
        self.assertOutput('!lulz', ['16 Feb 14h-15h : 1 lolz',
                                    '16 Feb 13h-14h : 1 lolz',
                                    ])

    def test_lol_kick(self):
        self.bot.send('lol', origin='michel')
        l = bot_kick(self.bot)
        self.assertIn('Au passage, michel est un sacré Kevin', l)
