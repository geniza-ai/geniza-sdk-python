from geniza.access import Access
from geniza.client import HttpClient
from geniza.config import Config


class Geniza:
    """Geniza.ai Python SDK"""

    def __init__(self, key: str, secret_key: str, sandbox_mode: bool = False):
        access = Access(key, secret_key)
        self.config = Config(access)
        self._client = HttpClient(self.config)

        if sandbox_mode:
            self.config.set_as_sandbox()

    def call_endpoint(self, endpoint: str, **kwargs):
        """
        This is a generic method to call Geniza endpoints.
        Parameters
        ----------
        endpoint:  The endpoint path
        kwargs: Any additional keyword arguments that are required for this endpoint.

        Returns the results of the call.
        -------

        """
        results = self._client.post(endpoint, kwargs)
        return results

    def ask_sapient_squirrel(self, question: str) -> str:
        """The Sapient Squirrel

        :param question: the question to ask the Sapient Squirrel
        :returns: the Sapient Squirrel's answer
        :rtype: str

        """
        payload = {'question': question}
        resp = self._client.post('sapientSquirrel', payload)
        return resp['answer']

    def provide_feedback(self, uuid: str, rating: float, feedback: str):
        """Provide feedback on a Geniza.ai response

        :param uuid: Unique Request ID
        :param rating: response quality rating from 0 (poor) to 1 (good)
        :param feedback: additional feedback

        """
        if rating < 0 or rating > 1:
            raise ValueError('Rating must be between 0 and 1')

        payload = {
            'uuid': uuid,
            'rating': rating,
            'feedback': feedback
        }
        self._client.post('feedback', payload)

    def extract_stock_symbols(self, text: str) -> dict:
        """
        This component accepts an article or some other text as input and extracts
        the company names and ticker symbols for that company.

        :param text: The input article or text.
        """
        if text is None or len(text) == 0:
            raise ValueError("You must supply text from which to extract stocks.")

        return self._client.post('extractors/stockSymbols', {'text': text})

    def detect_pii(self, text: str) -> dict:
        """
        This component accepts an article or some other text as input and detects any
        PII that may be present in the text.

        :param text: The input article or text.
        """
        if text is None or len(text) == 0:
            raise ValueError("You must supply text from which to detect PII.")

        return self._client.post('detectors/pii', {'text': text})

    def detect_language(self, text: str) -> dict:
        """
        This component accepts an article or some other text as input and detects what language
        the text is written in.

        :param text: The input article or text.
        """
        if text is None or len(text) == 0:
            raise ValueError("You must supply text from which to detect the language.")

        return self._client.post('detectors/language', {'text': text})
