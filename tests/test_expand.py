from unittest.mock import patch

import httpx

from tofbot.toflib import urls_in

from common import TofbotTestCase


_request = httpx.Request("GET", "test")

class TestExpand(TofbotTestCase):

    async def test_expand_tiny(self):
        shortened = "http://tinyurl.com/deadbeef"
        target = "http://google.fr/"

        def fake_response(url, cookies=None):
            if url == shortened:
                return httpx.Response(301, headers={"Location": target}, request=_request)
            elif url == target:
                return httpx.Response(200, request=_request)
            else:
                raise AssertionError(f"Unexpected URL: {url}")
            
        with patch("httpx.AsyncClient.get", side_effect=fake_response
        ) as mock_client:
            await self.assertOutput(f"Check out {shortened}", target)
            mock_client.assert_called_once_with(shortened, cookies={})


    async def test_expand_video(self):
        url = "https://www.youtube.com/watch?v=J---aiyznGQ"
        title = "Keyboard cat"
        response = "<html><head><title>%s</title></head></html>" % title
        with (patch("httpx.AsyncClient.get", return_value=httpx.Response(200, text=response, request=_request)) as mock_client,
             patch("httpx.AsyncClient.head", return_value=httpx.Response(200, request=httpx.Request("HEAD", url))) as mock_head):
            await self.assertOutput("Check out this video %s" % url, title)
            mock_client.assert_called_once_with(url, cookies={})
            mock_head.assert_called_once_with(url)

    async def test_expand_video_error(self):
        """
        If youtube returns an unparseable page, don't bail out.
        """
        url = "https://www.youtube.com/watch?v=J---aiyznGQ"
        with (patch("httpx.AsyncClient.get", return_value=httpx.Response(200, text="erger", request=_request)) as mock_client,
             patch("httpx.AsyncClient.head", return_value=httpx.Response(200, request=httpx.Request("HEAD", url))) as mock_head):
            await self.assertOutputLength("Check out %s" % url, 0)

    async def test_expand_mini_error(self):
        """
        If a minifier creates a redirect loop, don't bail out.
        """
        target = "http://tinyurl.com/deadbeef"
        with patch("httpx.AsyncClient.get", return_value=httpx.Response(301, headers={"Location": target}, request=_request)) as mock_client:
            await self.assertOutputLength("Check out %s" % target, 0)

    async def test_urls_in(self):
        """
        This example broke RE_URL.findall()
        taken from http://daringfireball.net/2010/07/improved_regex_for_matching_urls:
        RE_URL = re.compile(
            r"(?xi)
            \b
            (                           # Capture 1: entire matched URL
            (?:
                https?:                     # URL protocol and colon
                (?:
                /{1,3}                        # 1-3 slashes
                |                             #   or
                [a-z0-9%]                     # Single letter or digit or '%'
                                                # (Trying not to match e.g.
                                                # "URI::Escape")
                )
                |                           #   or
                www\d{0,3}[.]               # "www.", "www1.", "www2." … "www999."
                |                           #   or
                [a-z0-9.\-]+[.][a-z]{2,4}/  # looks like domain name followed by
                                            # a slash
            )
            (?:                           # One or more:
                [^\s()<>]+                      # Run of non-space, non-()<>
                |                               #   or
                \(([^\s()<>]+|(\([^\s()<>]+\)))*\)  # balanced parens, up to 2 levels
            )+
            (?:                           # End with:
                \(([^\s()<>]+|(\([^\s()<>]+\)))*\)  # balanced parens, up to 2 levels
                |                                   #   or
                [^\s`!()\[\]{};:'".,<>?«»“”‘’]        # not a space or one of these
                                                    # punct chars
            )
            )
            "
        )
        """
        target = """lorem ipsum dolor sit tofbot:
        https://fr.wikipedia.org/wiki/The_Agency_(s%C3%A9rie_t%C3%A9l%C3%A9vis%C3%A9e,_2024)
        haha lol
        """
        assert 1 == len(urls_in(target))
