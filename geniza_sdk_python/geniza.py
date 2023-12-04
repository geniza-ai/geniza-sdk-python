from geniza_sdk_python.client import HttpClient
from geniza_sdk_python.access import Access
from geniza_sdk_python.config import Config


class Geniza:
    """Geniza.ai Python SDK"""

    def __init__(self, key: str, secret_key: str, sandbox_mode: bool = False):
        access = Access(key, secret_key)
        self.config = Config(access)
        self._client = HttpClient(self.config)

        if sandbox_mode:
            self.config.set_as_sandbox()

    def ask_sapient_squirrel(self, question: str) -> str:
        """The Sapient Squirrel

        :param question: the question to ask the Sapient Squirrel
        :returns: the Sapient Squirrel's answer
        :rtype: str

        """
        payload = {'question': question}
        resp = self._client.post('sapientSquirrel', payload)
        return resp['answer']

    def provide_feedback(self, uuid: str, rating: float, add_feedback: str):
        """Provide feedback on a Geniza.ai response

        :param uuid: Unique Request ID
        :param rating: response quality rating from 0 (poor) to 1 (good)
        :param add_feedback: additional feedback

        """
        if rating < 0 or rating > 1:
            raise ValueError('Rating must be between 0 and 1')

        payload = {
            'uuid': uuid,
            'rating': rating,
            'feedback': add_feedback
        }
        self._client.post('feedback', payload)

    def extract_stock_symbols(self, text: str) -> list:
        """
        This component accepts an article or some other text as input and extracts
        the company names and ticker symbols for that company.

        :param text: The input article or text.
        """
        if text is None or len(text) == 0:
            raise ValueError("You must supply text from which to extract stocks.")

        return self._client.post('extractors/stock_symbols', {'text': text})
