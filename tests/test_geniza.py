import unittest
from geniza_sdk_python.geniza import Geniza
from httmock import urlmatch, HTTMock
from json import dumps, loads


class TestGeniza(unittest.TestCase):

    def setUp(self):

        key = '123'
        secret_key = 'xyz'

        self.geniza = Geniza(key, secret_key)
        # Override base URI to avoid name resolution and SSL errors during unit testing.
        self.geniza.config.base_uri = 'http://localhost/v1'

    @urlmatch(path=r'/sapientSquirrel$')
    def _mock_sapient_squirrel(self, url, request):
        req_parsed = loads(request.body)
        assert req_parsed['question'] == '1234567890'
        return dumps({'answer': 'qwerty'})

    def test_sapient_squirrel(self):
        with HTTMock(self._mock_sapient_squirrel):
            answer = self.geniza.ask_sapient_squirrel('1234567890')
            assert answer == 'qwerty'

    @urlmatch(path=r'/feedback$')
    def _mock_feedback(self, url, request):
        req_parsed = loads(request.body)
        assert req_parsed['uuid'] == '123'
        assert req_parsed['rating'] == 0.99999
        assert req_parsed['feedback'] == 'Fee fi fo fum'

        return dumps({})

    def test_feedback(self):
        with HTTMock(self._mock_feedback):
            self.geniza.provide_feedback('123', 0.99999, 'Fee fi fo fum')


if __name__ == '__main__':
    unittest.main()
