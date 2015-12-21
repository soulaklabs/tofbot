from common import TofbotTestCase, set_clock
from mock import patch


class TestRisoli(TofbotTestCase):

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
