from common import TofbotTestCase


class TestLag(TofbotTestCase):
    async def test_unknown_nick(self):
        await self.assertOutput("!lag kevin", "Pas d'infos sur kevin.")
        await self.assertOutput("!mentions kevin", "Pas d'infos sur kevin.")

    async def test_no_lag(self):
        await self.bot.send("hello!", origin="kevin")
        await self.assertOutput("!lag kevin", "Pas de lag pour kevin.")
