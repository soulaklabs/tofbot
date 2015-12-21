from common import TofbotTestCase, bot_action
from httpretty import HTTPretty, httprettified
from plugins.euler import EulerEvent


class TestEuler(TofbotTestCase):

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
