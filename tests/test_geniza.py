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

    @urlmatch(path=r'/v1/detectors/pii$')
    def _mock_pii_v1(self, url, request):
        req_parsed = loads(request.body)
        self.assertEqual(
            {'text': "We've paid The Home Depot for your purchase in full so you can spread your $297.46 USD purchase "
                     "into 4 payments. Here's your payment schedule: "
                     "$74.37 USD due today"
                     "$74.36 USD on January 3, 2024"
                     "$74.36 USD on January 18, 2024"
                     "$74.37 USD on February 2, 2024"
                     "Both the total purchase and your down payment amounts will appear in your PayPal activity, "
                     "but you're not being charged twice. If dates and amounts change for any reason, "
                     "we’ll let you know. There's nothing else you need to do right now. We'll automatically withdraw "
                     "your payments from: "
                     "BANK OF AMERICA, N.A."
                     "Bank Account x-1234"}, req_parsed)
        return dumps({
            "env": "testing", "version": "0.1.2", "messages": None,
            "uuid": "80fd58c78e782a7f950e10a713105e026557ea44d54fe",
            "pii": [{"category": "financial_identifiers",
                     "subcategory": "payment schedule", "identifier": "$74.37 USD on February 2, 2024"},
                    {"category": "financial_identifiers", "subcategory": "bank account number", "identifier": "x-1234"},
                    {"category": "financial_identifiers", "subcategory": "bank name",
                     "identifier": "BANK OF AMERICA, N.A."}]})

    def test_detect_pii(self):
        with HTTMock(self._mock_pii_v1):
            response = self.geniza.detect_pii(
                "We've paid The Home Depot for your purchase in full so you can spread your $297.46 USD purchase "
                "into 4 payments. Here's your payment schedule: "
                "$74.37 USD due today"
                "$74.36 USD on January 3, 2024"
                "$74.36 USD on January 18, 2024"
                "$74.37 USD on February 2, 2024"
                "Both the total purchase and your down payment amounts will appear in your PayPal activity, "
                "but you're not being charged twice. If dates and amounts change for any reason, we’ll let you know. "
                "There's nothing else you need to do right now. We'll automatically withdraw your payments from: "
                "BANK OF AMERICA, N.A."
                "Bank Account x-1234")

            self.assertIsNotNone(response["pii"])
            self.assertEqual(45, len(response['uuid']))
            self.assertIsNotNone(response["version"])


 @urlmatch(path=r'/v1/analyzers/productFeedback$')
    def _mock_product_feedback_v1(self, url, request):
        req_parsed = loads(request.body)
        self.assertEqual("Title: I really liked this book\n\nActually, I was looking for some other methodology."
                         "Nothing wrong with the book, may be I could not understand exactly what I wanted.",
                         req_parsed)

        return dumps({
            "env": "testing", "version": "0.1.2", "messages": None,
            "uuid": "80fd58c78e782a7f950e10a713105e026557ea44d54fe",
            "feedback": {"classification": "neutral", "confidence": 73}})

    def test_product_feedback_v1(self):
        """
        test function analyze_product_feedback
        """
        # test feedback
        with HTTMock(self._mock_product_feedback_v1):
            #     response = self.geniza.analyze_product_feedback(
            #         "Actually, I was looking for some other methodology. Nothing wrong with the book, may be I could not"
            #         "understand exactly what I wanted.")
            #
            #     self.assertIsNotNone(response['feedback'])
            #     self.assertEqual("neutral", response['feedback']['classification'])
            #     self.assertEqual(73, response['feedback']['confidence'])
            #     self.assertEqual(45, len(response['uuid']))
            #     self.assertIsNotNone(response['version'])

            # test feedback with title
            response = self.geniza.analyze_product_feedback(
                'Actually, I was looking for some other methodology. Nothing wrong with the book, may be I could not '
                'understand exactly what I wanted.',
                'I really liked this book'
            )

            self.assertIsNotNone(response['feedback'])
            self.assertEqual("neutral", response['feedback']['classification'])
            self.assertEqual(73, response['feedback']['confidence'])
            self.assertEqual(45, len(response['uuid']))
            self.assertIsNotNone(response['version'])



if __name__ == '__main__':
    unittest.main()
