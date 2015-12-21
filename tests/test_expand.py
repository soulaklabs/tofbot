from common import TofbotTestCase
from httpretty import HTTPretty, httprettified


class TestExpand(TofbotTestCase):

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
