import json
import logging
from typing import Any, Dict, Optional, Union

import httpx

log: logging.Logger = logging.getLogger(__name__)


class Utility:
    """Class containing utilitarian functions intended to reduce duplicate code."""

    def GET(
        self: Any,
        url: str,
        headers: Dict[str, str],
        parameters: Dict[str, str] = {"language": "en"},
    ) -> Optional[dict]:
        """
        Return the response of a successful HTTP GET request to the specified
        URL with the optionally provided header values.
        """

        res: httpx.Response = httpx.get(url, headers=headers, params=parameters)

        # HTTP 200 (OK)
        if res.status_code == 200:
            if res.headers["Content-Type"].lower() == "application/json; charset=utf-8":
                return res.json()
        else:
            log.error(f"Failed to GET {url} (HTTP {res.status_code})")

    def ReadFile(self: Any, filename: str, extension: str) -> Optional[dict]:
        """Read and return the contents of the specified file."""

        try:
            with open(f"{filename}.{extension}", "r", encoding="utf-8") as file:
                if extension == "json":
                    return json.loads(file.read())
        except Exception as e:
            log.error(f"Failed to read {filename}.{extension}, {e}")

    def WriteFile(
        self: Any, filename: str, extension: str, data: Union[str, dict, list]
    ) -> None:
        """Write the provided data to the specified file."""

        try:
            with open(f"{filename}.{extension}", "w", encoding="utf-8") as file:
                if extension == "json":
                    file.write(json.dumps(data, indent=4))
                else:
                    file.write(data)
        except Exception as e:
            log.error(f"Failed to write {filename}.{extension}, {e}")
