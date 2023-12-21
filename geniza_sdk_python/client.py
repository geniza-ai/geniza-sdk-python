from http import HTTPStatus
from json import dumps
from urllib.parse import urljoin
from sys import hexversion
import requests
from geniza.config.config import Config

FMT_AUTHZ = 'HMAC-SHA256 {}:{}'
FMT_USER_AGENT = 'Geniza.ai-SDK-Python/{}, Python/{}'


class HttpClient:
    """Handles making requests of Geniza web services"""

    def __init__(self, config: Config):
        self.config = config

    def post(self, url: str, payload: dict, add_headers: dict = None) -> dict:
        """Executes a POST against a Geniza service, see request method
        docstring for usage
        """
        return self.request('POST', url, payload, add_headers)

    def request(
            self,
            method: str,
            path: str,
            payload: dict,
            add_headers: dict = None
            ) -> dict:
        """Builds and executes a request against an Geniza service

        :param method: HTTPMethod: HTTP request method
        :param url: Geniza service endpoint
        :param payload: JSON serialisable Geniza service request data
        :param add_headers: additional HTTP request headers
        :return: deserialised response payload

        """
        message = _serialise(payload)
        hmac = self.config.access.hmac(message)

        std_headers = {
            'Accept': 'application/json',
            'Authorization': FMT_AUTHZ.format(self.config.access.key, hmac),
            'Content-Type': 'application/json',
            'User-Agent': FMT_USER_AGENT.format(Config.VERSION, hexversion)
        }

        # The user's additional headers come first in the dict union that
        # follows so that we overwrite any Geniza standard headers they may
        # have set with our own values.
        if add_headers is None:
            add_headers = {}

        headers = add_headers | std_headers

        final_url = self.config.get_full_api_path(url)
        response = requests.request(
            method,
            final_url,
            data=message,
            headers=headers,
            timeout=self.config.request_timeout_s
        )

        print(response.request.headers)
        print(response.request.body)

        if response.status_code != HTTPStatus.OK:
            raise RuntimeError('HTTP Status {}: {}'.format(
                response.status_code,
                response.text
            ))

        return response.json()


def _serialise(payload: dict) -> str:
    """Serialises a Geniza service request object to JSON

    :param payload: JSON serialisable Geniza service request data
    :return: payload serialised to JSON using the Geniza format conventions

    """
    # JSON payload formatting convention:
    # - Slashes should not be escaped
    # - Non-ASCII chars should not be escaped
    # - A null payload becomes the empty string

    if payload is None:
        return ''

    # The extra step below is needed to counteract the escaping of extended
    # chars by json.dumps(...)
    utf8_bytes = dumps(payload, ensure_ascii=False).encode('utf8')
    return utf8_bytes.decode()
