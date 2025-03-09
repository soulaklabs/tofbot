from common import TofbotTestCase, set_clock, bot_action
from unittest.mock import patch


class TestRisoli(TofbotTestCase):
    @patch("tofbot.plugins.risoli.datetime_now")
    async def test_risoli(self, now_mock):
        plugin = self.bot.plugins["risoli"]
        chan = "chan"
        gonze = "jean-michel"
        set_clock(now_mock, minutes=32)
        await plugin.on_join(chan, gonze)
        await self.bot.send("%s: 37" % self.bot.nick, origin="alice")
        await self.bot.send("%s: 35" % self.bot.nick, origin="bob")
        await self.bot.send("%s: 38" % self.bot.nick, origin="bob")
        await self.bot.send("%s: notanumber" % self.bot.nick, origin="mallory")
        await plugin.on_join(chan, "juan-carlo")

        async def jean_michel_quits():
            set_clock(now_mock, minutes=36)
            await plugin.on_quit(gonze)
        messages = await bot_action(self.bot, jean_michel_quits())
        self.assertEqual(messages, ["bob gagne un Point Internet"])

    @patch("tofbot.plugins.risoli.datetime_now")
    async def test_risoli_hour(self, now_mock):
        plugin = self.bot.plugins["risoli"]
        chan = "chan"
        other_gonze = "alberto"
        set_clock(now_mock, hours=2, minutes=59)
        await plugin.on_join(chan, other_gonze)
        await self.bot.send("%s: 13" % self.bot.nick, origin="carla")
        await self.bot.send("%s: 17" % self.bot.nick, origin="dylan")

        async def alberto_leaves():
            set_clock(now_mock, hours=3, minutes=15)
            await plugin.on_leave(chan, other_gonze)
        messages = await bot_action(self.bot, alberto_leaves())
        self.assertEqual(messages, ["carla gagne un Point Internet"])

    @patch("tofbot.plugins.risoli.datetime_now")
    async def test_risoli_nobody_wins(self, now_mock):
        plugin = self.bot.plugins["risoli"]
        chan = "chan"
        only_gonze = "tof"
        set_clock(now_mock, minutes=32)
        await plugin.on_join(chan, only_gonze)
        await self.bot.send("%s: 34" % self.bot.nick, origin="dylan")

        async def tof_leaves():
            await plugin.on_leave(chan, only_gonze)
        messages = await bot_action(self.bot, tof_leaves())
        self.assertEqual(messages, [])

    @patch("tofbot.plugins.risoli.datetime_now")
    async def test_risoli_same_hour(self, now_mock):
        plugin = self.bot.plugins["risoli"]
        chan = "chan"
        the_gonze = "alberto"
        set_clock(now_mock, minutes=34)
        await plugin.on_join(chan, the_gonze)
        await self.bot.send("%s: 35" % self.bot.nick, origin="a")
        await self.bot.send("%s: 33" % self.bot.nick, origin="b")
        await self.bot.send("%s: 38" % self.bot.nick, origin="c")

        async def alberto_leaves():
            set_clock(now_mock, minutes=35)
            await plugin.on_leave(chan, the_gonze)
        messages = await bot_action(self.bot, alberto_leaves())
        self.assertEqual(messages, ["a gagne un Point Internet"])

    async def test_risoli_overflow(self):
        plugin = self.bot.plugins["risoli"]
        await plugin.on_join("chan", "a")
        await self.bot.send("%s: 70" % self.bot.nick, origin="b")
