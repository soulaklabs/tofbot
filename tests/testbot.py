# -*- coding: utf-8 -*-

from httpretty import HTTPretty, httprettified
from plugins.jokes import TofadeEvent
from mock import patch
import json
from common import TestTofbot, TestOrigin, TofbotTestCase
from common import bot_input, bot_action, bot_kick


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


def set_clock(now_mock, hours=0, minutes=0):
    from datetime import datetime
    now_mock.return_value = datetime(1941, 2, 16, hours, minutes, 0, 0)


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
        self.bot.send('%s: 38' % self.bot.nick, origin="bob")
        self.bot.send('%s: notanumber' % self.bot.nick, origin="mallory")
        plugin.on_join(chan, 'juan-carlo')

        @self.assertOutputDo('bob gagne un Point Internet')
        def jean_michel_quits():
            set_clock(now_mock, minutes=36)
            plugin.on_quit(gonze)

    @patch('plugins.risoli.datetime_now')
    def test_risoli_hour(self, now_mock):
        plugin = self.bot.plugins['risoli']
        chan = 'chan'
        other_gonze = 'alberto'
        set_clock(now_mock, hours=2, minutes=59)
        plugin.on_join(chan, other_gonze)
        self.bot.send('%s: 13' % self.bot.nick, origin="carla")
        self.bot.send('%s: 17' % self.bot.nick, origin="dylan")

        @self.assertOutputDo('carla gagne un Point Internet')
        def alberto_leaves():
            set_clock(now_mock, hours=3, minutes=15)
            plugin.on_leave(chan, other_gonze)

    @patch('plugins.risoli.datetime_now')
    def test_risoli_nobody_wins(self, now_mock):
        plugin = self.bot.plugins['risoli']
        chan = 'chan'
        only_gonze = 'tof'
        set_clock(now_mock, minutes=32)
        plugin.on_join(chan, only_gonze)
        self.bot.send('%s: 34' % self.bot.nick, origin="dylan")

        @self.assertOutputDo([])
        def tof_leaves():
            plugin.on_leave(chan, only_gonze)

    @patch('plugins.risoli.datetime_now')
    def test_risoli_same_hour(self, now_mock):
        plugin = self.bot.plugins['risoli']
        chan = 'chan'
        the_gonze = 'alberto'
        set_clock(now_mock, minutes=34)
        plugin.on_join(chan, the_gonze)
        self.bot.send('%s: 35' % self.bot.nick, origin="a")
        self.bot.send('%s: 33' % self.bot.nick, origin="b")
        self.bot.send('%s: 38' % self.bot.nick, origin="c")

        @self.assertOutputDo('a gagne un Point Internet')
        def alberto_leaves():
            set_clock(now_mock, minutes=35)
            plugin.on_leave(chan, the_gonze)

    def test_risoli_overflow(self):
        plugin = self.bot.plugins['risoli']
        plugin.on_join('chan', 'a')
        self.bot.send('%s: 70' % self.bot.nick, origin="b")
