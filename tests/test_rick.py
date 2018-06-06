from common import TofbotTestCase
from httpretty import HTTPretty, httprettified


class TestRick(TofbotTestCase):

    @httprettified
    def test_rick(self):
        url = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
        title = 'rickroll'
        response = '<html><head><title>%s</title></head></html>' % title
        HTTPretty.register_uri(HTTPretty.GET, url, body=response)
        self.assertOutput("Keyboard cat v2: %s" % url,
                          [ "We're no strangers to love...", title ])
