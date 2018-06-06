import unittest
from bot import Tofbot
from collections import namedtuple


def print_resp(msg):
    print (" -> %s" % msg)


TestOrigin = namedtuple('TestOrigin', ['sender', 'nick'])


def bot_input(bot, msg):
    return bot_action(bot, lambda: bot.send(msg))


def bot_action(bot, action):
    msgs = []

    def capture_out(msg):
        msgs.append(msg)

    bot.cb = capture_out
    action()
    return msgs


def bot_kick(bot, msg=None):
    return bot_action(bot, lambda: bot.kick(msg))


def set_clock(now_mock, hours=0, minutes=0):
    from datetime import datetime
    now_mock.return_value = datetime(1941, 2, 16, hours, minutes, 0, 0)


class TestTofbot(Tofbot):

    def __init__(self, nick, name, chan, origin):
        chans = [chan]
        self.nick = nick
        Tofbot.__init__(self, nick, name, chans, debug=False)
        self.chan = chan
        self.origin = origin
        self.cb = None

    def msg(self, chan, msg):
        if self.cb:
            self.cb(msg)
        else:
            print_resp(msg)

    def send(self, msg, origin=None):
        """
        Send a message to the bot.
        origin is a string that overrides the sender's nick.
        """
        print ("<-  %s" % msg)
        if origin is None:
            origin = self.origin
        else:
            origin = TestOrigin('sender', origin)
        self.dispatch(origin, [msg, 'PRIVMSG', self.chan])

    def kick(self, msg=None):
        if msg is None:
            msg = self.nick
        self.dispatch(self.origin, [msg, 'KICK', self.chan, self.nick])


class TofbotTestCase(unittest.TestCase):

    def setUp(self):
        nick = "testbot"
        name = "Test Bot"
        chan = "#chan"
        self.origin = TestOrigin('sender', 'nick')
        self.bot = TestTofbot(nick, name, chan, self.origin)
        self.bot.joined = True
        cmds = ['!set autoTofadeThreshold 100']
        for cmd in cmds:
            bot_input(self.bot, cmd)

    def _find_event(self, clz):
        """
        Find an event of a given class in cron.
        """
        return ((k, v) for (k, v) in enumerate(self.bot.cron.events)
                if isinstance(v, clz)).next()

    def _delete_event(self, key):
        del self.bot.cron.events[key]

    def assertOutputDo(self, outp):
        if isinstance(outp, str):
            outp = [outp]

        def wrapper(f):
            line = bot_action(self.bot, lambda: f())
            self.assertEqual(line, outp)

        return wrapper

    def assertOutput(self, inp, outp):
        """
        Test that a given input produces a given output.
        """
        line = bot_input(self.bot, inp)
        if isinstance(outp, str):
            outp = [outp]
        self.assertEqual(line, outp)

    def assertOutputContains(self, inp, outp):
        """
        Test that a given input produces a given output (among others)
        """
        line = bot_input(self.bot, inp)
        if isinstance(outp, str):
            outp = [outp]
        for o in outp:
            self.assertIn(o, line)

    def assertOutputLength(self, msg, n):
        """
        Checks that when fed with msg, the bot's answer has length n.
        """
        line = bot_input(self.bot, msg)
        self.assertEqual(len(line), n)

    def assertNoOutput(self, msg):
        self.assertOutput(msg, [])
