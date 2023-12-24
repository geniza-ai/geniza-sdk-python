from geniza.access import Access


class Config():
    """ """
    _SB_BASE_URI = "https://sandbox.geniza.ai/"
    _PROD_BASE_URI = "https://api.geniza.ai/"
    _BASE_PATH = "v1/"
    VERSION = "0.1.2"

    def __init__(self, access: Access, request_timeout_s=10):
        super().__init__()

        self.base_uri = None
        self.access = access
        self.request_timeout_s = request_timeout_s
        self.set_as_production()

    def set_as_sandbox(self):
        """Points this client at the sandbox Geniza env"""
        self.base_uri = self._SB_BASE_URI + self._BASE_PATH

    def set_as_production(self):
        """Points this client at the production Geniza env"""
        self.base_uri = self._PROD_BASE_URI + self._BASE_PATH

    def get_full_api_path(self, url: str) -> str:
        """
        Returns the full api path.
        Parameters
        ----------
        url:  The input path.

        Returns
        -------
        The full URL for an API call.
        """
        return f"{self.base_uri}/{url}"
