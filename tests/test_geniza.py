import re
import unittest
from json import dumps, loads
from httmock import urlmatch, HTTMock
from geniza.geniza import Geniza


class TestGeniza(unittest.TestCase):

    def setUp(self):

        key = '123'
        secret_key = 'xyz'

        self.geniza = Geniza(key, secret_key)
        # Override base URI to avoid name resolution and SSL errors during unit testing.
        self.geniza.config.base_uri = 'http://localhost/v1'

    @urlmatch(path=r'/v1/sapientSquirrel$')
    def _mock_sapient_squirrel_v1(self, url, request):
        req_parsed = loads(request.body)
        self.assertEqual('1234567890', req_parsed['question'])
        return dumps({'answer': 'qwerty'})

    def test_sapient_squirrel_v1(self):
        with HTTMock(self._mock_sapient_squirrel_v1):
            answer = self.geniza.ask_sapient_squirrel('1234567890')
            self.assertEqual('qwerty', answer)

    @urlmatch(path=r'/v1/feedback$')
    def _mock_feedback_v1(self, url, request):
        req_parsed = loads(request.body)
        self.assertEqual('123', req_parsed['uuid'])
        self.assertEqual(0.99999, req_parsed['rating'])
        self.assertEqual('Fee fi fo fum', req_parsed['feedback'])

        return dumps({})

    def test_feedback_v1(self):
        with HTTMock(self._mock_feedback_v1):
            self.geniza.provide_feedback('123', 0.99999, 'Fee fi fo fum')

    @urlmatch(path=r'/v1/extractors/stockSymbols$')
    def _mock_extract_stock_v1(self, url, request):
        req_parsed = loads(request.body)
        results = re.search(r'(MSFT)', req_parsed['text'])
        self.assertEqual(1, len(results.groups()))

        return dumps(results.groups())

    def test_extract_stock_v1(self):
        with HTTMock(self._mock_extract_stock_v1):
            symbols = self.geniza.extract_stock_symbols(
                'MSFT has bought all of its employees Macbooks'
            )
            self.assertEqual(['MSFT'], symbols)


if __name__ == '__main__':
    unittest.main()
