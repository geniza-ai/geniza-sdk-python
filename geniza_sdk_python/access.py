import hmac
from hashlib import sha256


class Access():
    """Implements message authentication for Geniza service access."""
    def __init__(self, key, secret_key):
        self.key = key
        self._secret_key = secret_key

    def hmac(self, message: str) -> str:
        """Returns a SHA-256 HMAC for a UTF-8 message.

        :param message: input message for which the HMAC will be computed.
        :rtype str: the HMAC as hex digits

        """
        # We decode the message and secret key strings using utf-8. When the
        # resulting MAC hex string is put into the Authorization HTTP header
        # by the requests package it will probably be transcoded to latin-1.
        return hmac.new(
            bytes(self._secret_key, 'utf-8'),
            msg=bytes(message, 'utf-8'),
            digestmod=sha256
        ).hexdigest()
