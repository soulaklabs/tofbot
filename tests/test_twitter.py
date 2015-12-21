from common import TofbotTestCase
from httpretty import httprettified, HTTPretty


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


class TestTwitter(TofbotTestCase):

    @httprettified
    def test_twitter_expand(self):
        tweet_id = 1122334455667788
        tweet = 'Michel!'
        twitter_set_tweet('roflman', tweet, tweet_id)
        msg = 'https://twitter.com/roflman/status/%d' % tweet_id
        self.assertOutput(msg, tweet)
