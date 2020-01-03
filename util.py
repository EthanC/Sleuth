import logging

import requests

log = logging.getLogger(__name__)


class Utility:
    """Class containing utilitarian functions intended to reduce duplicate code."""

    def GET(self, url: str, headers: dict, parameters: dict = {"language": "en"}):
        """
        Return the response of a successful HTTP GET request to the specified
        URL with the optionally provided header values.
        """

        res = requests.get(url, headers=headers, params=parameters)

        # HTTP 200 (OK)
        if res.status_code == 200:
            return res.text
        else:
            log.critical(f"Failed to GET {url} (HTTP {res.status_code})")

    def ReadFile(self, filename: str, extension: str):
        """Read and return the contents of the specified file."""

        try:
            with open(f"{filename}.{extension}", "r", encoding="utf-8") as file:
                return file.read()
        except Exception as e:
            log.error(f"Failed to read {filename}.{extension}, {e}")

    def WriteFile(self, filename: str, extension: str, data: str):
        """Write the provided data to the specified file."""

        try:
            with open(f"{filename}.{extension}", "w", encoding="utf-8") as file:
                file.write(data)
        except Exception as e:
            log.error(f"Failed to write {filename}.{extension}, {e}")
