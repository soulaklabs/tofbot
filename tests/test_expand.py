from unittest.mock import patch

import httpx

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
