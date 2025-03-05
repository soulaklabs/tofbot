from unittest.mock import patch
from common import TofbotTestCase


class TestRick(TofbotTestCase):
    def test_rick(self):
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        with patch("httpx.AsyncClient.get"), patch("httpx.AsyncClient.head"):
            self.assertOutputContains(
                "Keyboard cat v2: %s" % url, ["We're no strangers to love..."]
            )
