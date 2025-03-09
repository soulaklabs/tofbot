from common import TofbotTestCase


class TestEuler(TofbotTestCase):
    async def test_jokes_misc(self):
        for cmd in ["fortune", "chuck", "contrepeterie"]:
            await self.assertOutputLength("!%s" % cmd, 1)

    async def test_jokes_butters(self):
        await self.bot.send("!set autoTofadeThreshold 0")
        await self.assertOutputContains(
            "hey %s how are you" % self.bot.nick,
            "%s: Ouais, c'est moi !" % self.origin.nick,
        )
        await self.bot.send("!set autoTofadeThreshold 9000")

    async def test_joke_riddle(self):
        await self.assertOutputLength("!devinette", 1)
        await self.bot.send("answer?")
