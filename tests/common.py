import unittest
from tofbot import Tofbot
from collections import namedtuple


def print_resp(msg):
    print(" -> %s" % msg)


TestOrigin = namedtuple("TestOrigin", ["sender", "nick"])
TestOrigin.__test__ = False


async def bot_input(bot, msg):
    return await bot_action(bot, bot.send(msg))


async def bot_action(bot, action):
    msgs = []

    def capture_out(msg):
        msgs.append(msg)

    bot.cb = capture_out
    if action:
        await action
    return msgs


async def bot_kick(bot, msg=None):
    return await bot_action(bot, bot.kick(msg))


def set_clock(now_mock, hours=0, minutes=0):
    from datetime import datetime

    now_mock.return_value = datetime(1941, 2, 16, hours, minutes, 0, 0)


class TestTofbot(Tofbot):
    __test__ = False

    def __init__(self, nick, name, chan, origin):
        chans = [chan]
        self.nick = nick
        Tofbot.__init__(self, nick, name, chans, debug=False)
        self.chan = chan
        self.origin = origin
        self.cb = None
        # self.verbose = True

    async def msg(self, chan, msg):
        if self.cb:
            self.cb(msg)
        else:
            print_resp(msg)

    async def send(self, msg, origin=None):
        """
        Send a message to the bot.
        origin is a string that overrides the sender's nick.
        """
        if origin is None:
            origin = self.origin
        else:
            origin = TestOrigin("sender", origin)
        await self.dispatch(origin, [msg, "PRIVMSG", self.chan])

    async def kick(self, msg=None):
        if msg is None:
            msg = self.nick
        await self.dispatch(self.origin, [msg, "KICK", self.chan, self.nick])


class TofbotTestCase(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        nick = "testbot"
        name = "Test Bot"
        chan = "#chan"
        self.origin = TestOrigin("sender", "nick")
        self.bot = TestTofbot(nick, name, chan, self.origin)
        self.bot.joined = True
        self.bot.autoTofadeThreshold = 100

    def _find_event(self, clz):
        """
        Find an event of a given class in cron.
        """
        return next(
            (k, v) for (k, v) in enumerate(self.bot.cron.events) if isinstance(v, clz)
        )

    def _delete_event(self, key):
        del self.bot.cron.events[key]

    async def assertOutput(self, inp, outp):
        """
        Test that a given input produces a given output.
        """
        line = await bot_input(self.bot, inp)
        if isinstance(outp, str):
            outp = [outp]
        self.assertEqual(line, outp)

    async def assertOutputContains(self, inp, outp):
        """
        Test that a given input produces a given output (among others)
        """
        line = await bot_input(self.bot, inp)
        if isinstance(outp, str):
            outp = [outp]
        for o in outp:
            self.assertIn(o, line)

    async def assertOutputLength(self, msg, n):
        """
        Checks that when fed with msg, the bot's answer has length n.
        """
        line = await bot_input(self.bot, msg)
        self.assertEqual(len(line), n)

    def assertNoOutput(self, msg):
        self.assertOutput(msg, [])
