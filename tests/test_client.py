import re
import unittest
from json import dumps, loads
from httmock import urlmatch, HTTMock
from geniza.access import Access
from geniza.config import Config
from geniza.client import HttpClient, _serialise

TEST_ENDPOINT = 'post_endpoint'
TEST_ENDPOINT_REGEX = f'/{TEST_ENDPOINT}$'


class TestClient(unittest.TestCase):
    """"""
    API_KEY = '123'
    API_SECRET = 'xyz'
    ADD_HEADER = {'X-Geniza-Custom-Header': 'FooBar'}
    TEST_PAYLOAD = {'a': 1, 'b': 'two/2🍍', 'c': None}

    def setUp(self):
        access = Access(self.API_KEY, self.API_SECRET)
        config = Config(access)
        # Override base URI to avoid name resolution and SSL errors during unit testing.
        config.base_uri = 'http://localhost/v1'

        self.client = HttpClient(config)

    def test_ser_null(self):
        ser = _serialise(None)
        self.assertEqual('', ser, 'A null payload becomes the empty string')

    def test_set_ext_char(self):
        ser = _serialise(self.TEST_PAYLOAD)
        self.assertFalse(
            '\\' in ser,
            'Neither extended chars nor slashes should be escaped.'
        )

    @urlmatch(path=TEST_ENDPOINT_REGEX)
    def _mock_post_payload(self, url, request):
        req_parsed = loads(request.body)
        self.assertEqual(self.TEST_PAYLOAD, req_parsed)
        return dumps(self.TEST_PAYLOAD)

    def test_post_payload(self):
        with HTTMock(self._mock_post_payload):
            resp_parsed = self.client.post(TEST_ENDPOINT, self.TEST_PAYLOAD)
            self.assertEqual(self.TEST_PAYLOAD, resp_parsed)

    @urlmatch(path=TEST_ENDPOINT_REGEX)
    def _mock_add_headers(self, url, request):
        self.assertEqual(
            self.ADD_HEADER['X-Geniza-Custom-Header'],
            request.headers['X-Geniza-Custom-Header']
        )

        return "{}"

    def test_add_headers(self):
        with HTTMock(self._mock_add_headers):
            _ = self.client.post(TEST_ENDPOINT, None, add_headers=self.ADD_HEADER)

    @urlmatch(path=TEST_ENDPOINT_REGEX)
    def _mock_std_headers(self, url, request):
        self.assertEqual('application/json', request.headers['Accept'])
        self.assertEqual('application/json', request.headers['Content-Type'])
        self.assertRegex(
            request.headers['User-Agent'],
            r'Geniza.ai-SDK-Python/.+, Python/.+'
        )
        return "{}"

    def test_std_headers(self):
        with HTTMock(self._mock_std_headers):
            _ = self.client.post(TEST_ENDPOINT, None)

    @urlmatch(path=TEST_ENDPOINT_REGEX)
    def _mock_auth_header(self, url, request):
        hmac_header = request.headers['Authorization']
        result = re.search(r'^HMAC-SHA256 (\w+):(\w+)$', hmac_header)
        self.assertEqual(self.API_KEY, result.group(1))
        hmac_expected = self.client.config.access.hmac(request.body)
        self.assertEqual(hmac_expected, result.group(2))

        return "{}"

    def test_auth_header(self):
        with HTTMock(self._mock_auth_header):
            _ = self.client.post(TEST_ENDPOINT, self.TEST_PAYLOAD)


if __name__ == '__main__':
    unittest.main()
