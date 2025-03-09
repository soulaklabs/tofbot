from common import bot_input, bot_kick, set_clock, TofbotTestCase


class TestCase(TofbotTestCase):
    def test_set_allowed(self):
        msg = "!set autoTofadeThreshold 9000"
        await self.bot.send(msg)
        self.assertOutput("!get autoTofadeThreshold", "autoTofadeThreshold = 9000")

    def test_kick(self):
        line = bot_kick(self.bot)
        self.assertEqual(line, ["respawn, LOL"])

    def test_kick_reason(self):
        line = bot_kick(self.bot, "tais toi")
        self.assertEqual(line, ["comment ça, tais toi ?"])

    def test_dassin(self):
        self.assertOutput("tu sais", "je n'ai jamais été aussi heureux que ce matin-là")

    def test_donnezmoi(self):
        self.assertOutput("donnez moi un lol", ["L", "O", "L"])

    def test_eightball(self):
        self.assertOutputLength("boule magique, est-ce que blabla ?", 1)

    def test_sed(self):
        await self.bot.send("oho")
        self.assertOutput("s/o/a", "<%s> : aha" % self.origin.nick)

    def test_sed_invalid(self):
        await self.bot.send("oho")
        self.assertNoOutput("s/++/a")

    def test_like(self):
        self.assertOutputLength("!ggg", 0)
        await self.bot.send("oh oh", origin="alfred")
        await self.bot.send("!like")
        self.assertOutput("!score michel", "michel n'a pas de starz.")

    def test_elle(self):
        del self.bot.plugins["jokes"]
        await self.bot.send("!set autoTofadeThreshold 0")
        self.assertOutputContains("elle a les yeux revolver", "Le vrai win c'est ♥")
