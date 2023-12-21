from geniza.config.access import Access
from geniza.config.base_config import BaseConfig


class Config(BaseConfig):
    """ """
    def __init__(self, access: Access):
        super().__init__()

        self._sb_base_uri = "https://sandbox.geniza.ai/"
        self._prod_base_uri = "https://api.geniza.ai/"
        self._base_path = "v1/"

        self.base_uri = None
        self.access = access
        self.version = "0.1.2"
        self.request_timeout_s = 10  # TODO: How long might Geniza requests need?

        self.set_as_production()

    def set_as_sandbox(self):
        """Points this client at the sandbox Geniza env"""
        self.base_uri = self._sb_base_uri + self._base_path

    def set_as_production(self):
        """Points this client at the production Geniza env"""
        self.base_uri = self._prod_base_uri + self._base_path

    def get_full_api_path(self, path: str) -> str:
        """
        Creates the final api path for the API call.
        Parameters
        ----------
        path:  The input path for the API call.

        Returns:  The final URL for the API call.
        -------

        """
        return f"{self.base_uri}{path}"
