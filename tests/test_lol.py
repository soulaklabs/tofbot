from common import TofbotTestCase, set_clock, bot_kick
from unittest.mock import patch


class TestLol(TofbotTestCase):
    async def test_lol_kevin(self):
        await self.assertOutput("!kevin", "pas de Kevin")
        for msg in ["lol", "lolerie"]:
            await self.bot.send(msg, origin="michel")
        await self.assertOutput("!kevin", "michel est le Kevin du moment avec 2 lolades")
        for msg in ["lulz", "LOL", "10L"]:
            await self.bot.send(msg, origin="alfred")
        await self.assertOutput("!kevin", "alfred est le Kevin du moment avec 3 lolades")

    @patch("tofbot.plugins.lolrate.datetime_now")
    async def test_lol_rate(self, now_mock):
        await self.bot.send("!set lolRateDepth 2")
        await self.assertOutput("!get lolRateDepth", "lolRateDepth = 2")

        set_clock(now_mock, 12)
        await self.bot.send("lol")
        await self.bot.send("lol")
        expected = "16 Feb 12h-13h : 2 lolz"
        await self.assertOutput("!lulz", expected)
        # check that the command itself does not increment
        await self.assertOutput("!lulz", expected)

        set_clock(now_mock, 13)
        await self.bot.send("lol")
        await self.assertOutput(
            "!lulz",
            [
                "16 Feb 13h-14h : 1 lolz",
                expected,
            ],
        )

        set_clock(now_mock, 14)
        await self.bot.send("lol")
        await self.assertOutput(
            "!lulz",
            [
                "16 Feb 14h-15h : 1 lolz",
                "16 Feb 13h-14h : 1 lolz",
            ],
        )

    async def test_lol_kick(self):
        await self.bot.send("lol", origin="michel")
        line = await bot_kick(self.bot)
        self.assertIn("Au passage, michel est un sacré Kevin", line)
