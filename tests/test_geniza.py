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

    @urlmatch(path=r'/v1/summarizers/messageSummary$')
    def _mock_summary_v1(self, url, request):
        # test that it sent correct message
        req_parsed = loads(request.body)
        self.assertEqual(
            {"message": "As a Wisconsin Medical Center (WIMC), [CUSTOMER] knows that communication failure is a "
                        "leading source of adverse events in health care. Indeed, the Joint Commission on "
                        "Accreditation of Healthcare Organizations (JCAHO) identified communication failure as a "
                        "pivotal factor in over 70% of more than 3.000 sentinel event reports since 1995. As of March "
                        "2006, nearly 80% of more than 6,000 Root Cause Analysis reports to the WI National Center for "
                        "Patient Safety (NCPS) involve communication failure as at least one of the primary factors "
                        "contributing to adverse events and close calls. Following the suggestion from the Institute "
                        "of Medicine (IOM) report \"To Err Is Human: Building a Safer Healthcare System\", "
                        "recommending teamwork training to improve communication for health care organizations, "
                        "Milwaukee Health Academy, Inc. (MHAI) began developing a Medical Team Training (MTT) program "
                        "in 2003. This program was designed to introduce communication tools to professionals working "
                        "in WI facilities -- tools which they can integrate into their clinical workplace."
                        "The program you can subscribe to comprises three important components: "
                        "1. Application, preparation, and planning;"
                        "2. Learning sessions at the WIMC; and"
                        "3. Follow-up data collection and support from involved WIMCs."
                        "As of April 2006, 19 facilities were participating in the program, involving clinical units "
                        "such as the OR (10), ICU (4), Medical-Surgery Unit (1), Ambulatory Clinics (3), and ED (1). "
                        "The Safety Attitudes Questionnaire (SAQ), developed and validated by the Johns Hopkins "
                        "Quality and Safety Research Group, was completed by each participant prior to commencing the "
                        "session, and repeated one year later. The SAQ measured a significant change in attitude and "
                        "behavior regarding six factors: safety climate, teamwork climate, job satisfaction, working "
                        "conditions, perceptions of management, and stress recognition. Choosing [PROVIDER]'s training "
                        "program to implement MTT communication principles in health care delivery will improve "
                        "outcomes for your patients while rewarding your employees in the accomplishment of their "
                        "daily tasks. When you consider the changes observed against the six factors mentioned above, "
                        "you come to the conclusion that [CUSTOMER] will get significant benefits in selecting "
                        "[PROVIDER] to train its caregivers to better deliver care services to the patient community.",
             'wordCount': 10},
            req_parsed)

        return dumps({"env": "testing", "version": "0.4.0", "messages": None,
                      "uuid": "80fd58c78e782a7f950e10a713105e026557ea44d54fe",
                      "message": {"summary": "The flies in the back room have been completely eliminated",
                                  "wordCount": 10}})

    def test_message_summary_v1(self):
        """
        test function message_summary
        """
        with HTTMock(self._mock_summary_v1):
            response = self.geniza.message_summary(
                "As a Wisconsin Medical Center (WIMC), [CUSTOMER] knows that communication failure is a leading "
                "source of adverse events in health care. Indeed, the Joint Commission on Accreditation of Healthcare "
                "Organizations (JCAHO) identified communication failure as a pivotal factor in over 70% of more than "
                "3.000 sentinel event reports since 1995. As of March 2006, nearly 80% of more than 6,000 Root Cause "
                "Analysis reports to the WI National Center for Patient Safety (NCPS) involve communication failure as "
                "at least one of the primary factors contributing to adverse events and close calls. Following the "
                "suggestion from the Institute of Medicine (IOM) report \"To Err Is Human: Building a Safer Healthcare "
                "System\", recommending teamwork training to improve communication for health care organizations, "
                "Milwaukee Health Academy, Inc. (MHAI) began developing a Medical Team Training (MTT) program in 2003. "
                "This program was designed to introduce communication tools to professionals working in WI facilities "
                "-- tools which they can integrate into their clinical workplace."
                "The program you can subscribe to comprises three important components: "
                "1. Application, preparation, and planning;"
                "2. Learning sessions at the WIMC; and"
                "3. Follow-up data collection and support from involved WIMCs."
                "As of April 2006, 19 facilities were participating in the program, involving clinical units such as "
                "the OR (10), ICU (4), Medical-Surgery Unit (1), Ambulatory Clinics (3), and ED (1). The Safety "
                "Attitudes Questionnaire (SAQ), developed and validated by the Johns Hopkins Quality and Safety "
                "Research Group, was completed by each participant prior to commencing the session, and repeated one "
                "year later. The SAQ measured a significant change in attitude and behavior regarding six factors: "
                "safety climate, teamwork climate, job satisfaction, working conditions, perceptions of management, "
                "and stress recognition. Choosing [PROVIDER]'s training program to implement MTT communication "
                "principles in health care delivery will improve outcomes for your patients while rewarding your "
                "employees in the accomplishment of their daily tasks. When you consider the changes observed against "
                "the six factors mentioned above, you come to the conclusion that [CUSTOMER] will get significant "
                "benefits in selecting [PROVIDER] to train its caregivers to better deliver care services to the "
                "patient community.", 10)

            # test response
            self.assertIsNotNone(response)
            self.assertEqual(45, len(response["uuid"]))
            self.assertEqual("The flies in the back room have been completely eliminated",
                             response["message"]["summary"])
            self.assertEqual(10, response["message"]["wordCount"])
            self.assertIsNotNone(response["version"])



if __name__ == '__main__':
    unittest.main()
