from api.client import HttpClient
from config import Access
from config import Config


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
        return self._client.post('sapientSquirrel', {'question': question})

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
