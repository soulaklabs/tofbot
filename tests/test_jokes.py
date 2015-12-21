from common import TofbotTestCase, bot_action
from plugins.jokes import TofadeEvent


class TestEuler(TofbotTestCase):

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
