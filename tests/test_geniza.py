import re
import unittest
from json import dumps, loads

from httmock import urlmatch, HTTMock
from geniza import Geniza


@urlmatch(path=r'(.*\.)?sapientSquirrel$', method='post')
def mock_sapient_squirrel(url, request):
    req_parsed = loads(request.body)
    #assertEqual('1234567890', req_parsed['question'])
    return dumps({'answer': 'qwerty'})


class TestGeniza(unittest.TestCase):

    def setUp(self):
        key = '123'
        secret_key = 'xyz'

        self.geniza = Geniza(key, secret_key)
        # Override base URI to avoid name resolution and SSL errors during unit testing.
        #self.geniza.config.base_uri = 'http://localhost/v1'

    def test_sapient_squirrel(self):
        with HTTMock(mock_sapient_squirrel):
            answer = self.geniza.ask_sapient_squirrel('1234567890')
            self.assertEqual('qwerty', answer)

    @urlmatch(path=r'/feedback$')
    def _mock_feedback(self, url, request):
        req_parsed = loads(request.body)
        self.assertEqual('123', req_parsed['uuid'])
        self.assertEqual(0.99999, req_parsed['rating'])
        self.assertEqual('Fee fi fo fum', req_parsed['feedback'])

        return dumps({})

    def test_feedback(self):
        with HTTMock(self._mock_feedback):
            self.geniza.provide_feedback('123', 0.99999, 'Fee fi fo fum')

    @urlmatch(path=r'/extractors/stock_symbols$')
    def _mock_extract_stock(self, url, request):
        req_parsed = loads(request.body)
        results = re.search(r'(MSFT)', req_parsed['text'])
        self.assertEqual(1, len(results.groups()))

        return dumps(results.groups())

    def test_extract_stock(self):
        with HTTMock(self._mock_extract_stock):
            symbols = self.geniza.extract_stock_symbols(
                'MSFT has bought all of its employees Macbooks'
            )
            self.assertEqual(['MSFT'], symbols)


if __name__ == '__main__':
    unittest.main()
