# -*- coding: utf-8 -*-

from httpretty import HTTPretty, httprettified
import json
from common import TestTofbot, TestOrigin, TofbotTestCase
from common import bot_input, bot_kick, set_clock


class TestCase(TofbotTestCase):

    def test_set_allowed(self):
        msg = "!set autoTofadeThreshold 9000"
        self.bot.send(msg)
        self.assertOutput("!get autoTofadeThreshold",
                          "autoTofadeThreshold = 9000")

    def test_kick(self):
        l = bot_kick(self.bot)
        self.assertEqual(l, ["respawn, LOL"])

    def test_kick_reason(self):
        l = bot_kick(self.bot, "tais toi")
        self.assertEqual(l, ["comment ça, tais toi ?"])

    def test_dassin(self):
        self.assertOutput("tu sais",
                          "je n'ai jamais été aussi heureux que ce matin-là")

    def test_donnezmoi(self):
        self.assertOutput("donnez moi un lol", ['L', 'O', 'L'])

    def test_eightball(self):
        self.assertOutputLength("boule magique, est-ce que blabla ?", 1)

    def test_sed(self):
        self.bot.send("oho")
        self.assertOutput("s/o/a", "<%s> : aha" % self.origin.nick)

    def test_sed_invalid(self):
        self.bot.send("oho")
        self.assertNoOutput("s/++/a")

    def test_like(self):
        self.assertOutputLength('!ggg', 0)
        self.bot.send('oh oh', origin='alfred')
        self.bot.send('!like')
        self.assertOutput('!ggg',
                          "alfred est le Good Guy Greg du moment avec 3.0 "
                          "starz de moyenne")
        self.assertOutput('!score alfred', 'alfred: 3.0 starz de moyenne.')
        self.assertOutput('!score michel', "michel n'a pas de starz.")

    def test_elle(self):
        del self.bot.plugins["jokes"]
        self.bot.send("!set autoTofadeThreshold 0")
        self.assertOutputContains(
                "elle a les yeux revolver",
                "Le vrai win c'est ♥")
