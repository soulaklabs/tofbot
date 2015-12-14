# -*- coding: utf-8 -*-

from bot import Tofbot
import unittest
from collections import namedtuple
from httpretty import HTTPretty, httprettified
from plugins.euler import EulerEvent
from plugins.jokes import TofadeEvent
from mock import patch
import json

TestOrigin = namedtuple('TestOrigin', ['sender', 'nick'])


def print_resp(msg):
    print (" -> %s" % msg)


def twitter_set_tweet(name, tweet, tweet_id):
    url = 'https://twitter.com/{screen_name}/status/{tweet_id}' \
          .format(screen_name=name,
                  tweet_id=tweet_id)
    html = """
        <html>
            <body>
               <div class='permalink-tweet'>
                    <p class='js-tweet-text'>
                        {tweet}
                    </p>
               </div>
            </body>
        </html>
        """.format(tweet=tweet)
    HTTPretty.register_uri(HTTPretty.GET, url, body=html)


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


def bot_action(bot, action):
    msgs = []

    def capture_out(msg):
        msgs.append(msg)

    bot.cb = capture_out
    action()
    return msgs


def bot_input(bot, msg):
    return bot_action(bot, lambda: bot.send(msg))


def bot_kick(bot, msg=None):
    return bot_action(bot, lambda: bot.kick(msg))


def set_clock(now_mock, hours=0, minutes=0):
    from datetime import datetime
    now_mock.return_value = datetime(1941, 2, 16, hours, minutes, 0, 0)


class TestCase(unittest.TestCase):

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

    def assertOutputDo(self, outp):
        if isinstance(outp, str):
            outp = [outp]

        def wrapper(f):
            l = bot_action(self.bot, lambda: f())
            self.assertEqual(l, outp)

        return wrapper

    def assertOutput(self, inp, outp):
        """
        Test that a given input produces a given output.
        """
        l = bot_input(self.bot, inp)
        if isinstance(outp, str):
            outp = [outp]
        self.assertEqual(l, outp)

    def assertOutputLength(self, msg, n):
        """
        Checks that when fed with msg, the bot's answer has length n.
        """
        l = bot_input(self.bot, msg)
        self.assertEqual(len(l), n)

    def assertNoOutput(self, msg):
        self.assertOutput(msg, [])

    def _find_event(self, clz):
        """
        Find an event of a given class in cron.
        """
        return ((k, v) for (k, v) in enumerate(self.bot.cron.events)
                if isinstance(v, clz)).next()

    def _delete_event(self, key):
        del self.bot.cron.events[key]

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

    @httprettified
    def test_euler(self):
        euler_nick = 'leonhard'

        def set_score(score):
            url = "http://projecteuler.net/profile/%s.txt" % euler_nick
            country = 'country'
            language = 'language'
            level = 1
            text = "%s,%s,%s,Solved %d,%d" % (euler_nick,
                                              country,
                                              language,
                                              score,
                                              level,
                                              )
            HTTPretty.register_uri(HTTPretty.GET, url,
                                   body=text,
                                   content_type="text/plain")

        set_score(10)
        self.bot.send("!euler_add leonhard")

        # Get event to unschedule and manually fire it
        (event_k, event) = self._find_event(EulerEvent)
        self._delete_event(event_k)

        self.assertOutput("!euler", "leonhard : Solved 10")
        set_score(15)
        l = bot_action(self.bot, event.fire)
        self.assertEqual(l, ["leonhard : Solved 10 -> Solved 15"])

    @httprettified
    def test_expand_tiny(self):
        url = 'http://tinyurl.com/deadbeef'
        target = 'http://google.fr/'

        HTTPretty.register_uri(HTTPretty.GET, url,
                               status=301,
                               location=target,
                               )

        HTTPretty.register_uri(HTTPretty.GET, target,
                               status=200,
                               )

        self.assertOutput("Check out %s" % url, target)

    @httprettified
    def test_expand_video(self):
        url = 'https://www.youtube.com/watch?v=J---aiyznGQ'
        title = 'Keyboard cat'
        response = '<html><head><title>%s</title></head></html>' % title
        HTTPretty.register_uri(HTTPretty.GET, url,
                               body=response,
                               )
        self.assertOutput("Check out this video %s" % url, title)

    @httprettified
    def test_expand_video_error(self):
        """
        If youtube returns an unparseable page, don't bail out.
        """
        url = 'https://www.youtube.com/watch?v=J---aiyznGQ'
        HTTPretty.register_uri(HTTPretty.GET, url, body='', )
        self.assertOutputLength("Check out %s" % url, 0)

    @httprettified
    def test_expand_mini_error(self):
        """
        If a minifier creates a redirect loop, don't bail out.
        """
        url = 'http://tinyurl.com/deadbeef'
        target = url
        HTTPretty.register_uri(HTTPretty.GET, url,
                               status=301,
                               location=target,
                               )
        self.assertOutputLength("Check out %s" % url, 0)

    def test_jokes_autotofade(self):
        (event_k, event) = self._find_event(TofadeEvent)

        self.bot.send('!set autoTofadeThreshold 0')
        l = bot_action(self.bot, event.fire)
        self.assertEqual(len(l), 1)
        self.bot.send('!set autoTofadeThreshold 9000')

    def test_jokes_misc(self):
        for cmd in ['fortune', 'chuck', 'tofade', 'contrepeterie']:
            self.assertOutputLength('!%s' % cmd, 1)

    def test_jokes_butters(self):
        self.bot.send('!set autoTofadeThreshold 0')
        self.assertOutput("hey %s how are you" % self.bot.nick,
                          "%s: Ouais, c'est moi !" % self.origin.nick)
        self.bot.send('!set autoTofadeThreshold 9000')

    def test_joke_riddle(self):
        self.assertOutputLength("!devinette", 1)
        self.bot.send('answer?')

    def test_sed(self):
        self.bot.send("oho")
        self.assertOutput("s/o/a", "<%s> : aha" % self.origin.nick)

    def test_sed_invalid(self):
        self.bot.send("oho")
        self.assertNoOutput("s/++/a")

    @httprettified
    def test_rick(self):
        url = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
        title = 'rickroll'
        response = '<html><head><title>%s</title></head></html>' % title
        HTTPretty.register_uri(HTTPretty.GET, url,
                               body=response,
                               )
        self.assertOutput("Keyboard cat v2: %s" % url,
                          [title,
                           "We're no strangers to love..."
                           ])

    def test_like(self):
        self.assertOutputLength('!ggg', 0)
        self.bot.send('oh oh', origin='alfred')
        self.bot.send('!like')
        self.assertOutput('!ggg',
                          "alfred est le Good Guy Greg du moment avec 3.0 "
                          "starz de moyenne")
        self.assertOutput('!score alfred', 'alfred: 3.0 starz de moyenne.')
        self.assertOutput('!score michel', "michel n'a pas de starz.")

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

    def test_ponce(self):
        del self.bot.plugins["jokes"]
        self.bot.send("!set autoTofadeThreshold 0")
        self.assertOutput("elle a les yeux revolver", "C'est ta meuf?")

    @httprettified
    def test_twitter_expand(self):
        tweet_id = 1122334455667788
        tweet = 'Michel!'
        twitter_set_tweet('roflman', tweet, tweet_id)
        msg = 'https://twitter.com/roflman/status/%d' % tweet_id
        self.assertOutput(msg, tweet)

    @patch('plugins.risoli.datetime_now')
    def test_risoli(self, now_mock):
        plugin = self.bot.plugins['risoli']
        chan = 'chan'
        gonze = 'jean-michel'
        set_clock(now_mock, minutes=32)
        plugin.on_join(chan, gonze)
        self.bot.send('%s: 37' % self.bot.nick, origin="alice")
        self.bot.send('%s: 35' % self.bot.nick, origin="bob")
        self.bot.send('%s: notanumber' % self.bot.nick, origin="mallory")
        plugin.on_join(chan, 'juan-carlo')

        @self.assertOutputDo('bob gagne un Point Internet')
        def jean_michel_quits():
            set_clock(now_mock, minutes=36)
            plugin.on_quit(gonze)

        other_gonze = 'alberto'
        set_clock(now_mock, hours=2, minutes=59)
        plugin.on_join(chan, other_gonze)
        self.bot.send('%s: 13' % self.bot.nick, origin="carla")
        self.bot.send('%s: 17' % self.bot.nick, origin="dylan")

        @self.assertOutputDo('carla gagne un Point Internet')
        def alberto_leaves():
            set_clock(now_mock, hours=3, minutes=15)
            plugin.on_leave(chan, other_gonze)

        only_gonze = 'tof'
        set_clock(now_mock, minutes=32)
        plugin.on_join(chan, only_gonze)
        self.bot.send('%s: 34' % self.bot.nick, origin="dylan")

        @self.assertOutputDo([])
        def tof_leaves():
            plugin.on_leave(chan, only_gonze)
