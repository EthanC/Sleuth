import requests
from PIL import Image, ImageFont

from logger import Log


class Utility:
    """Class containing utilitarian functions intended to reduce duplicate code."""

    def GET(self, url: str, headers={}):
        """
        Return the response of a successful HTTP GET request to the specified
        URL with the optionally provided header values.
        """

        res = requests.get(url, headers=headers)

        # HTTP 200 (OK)
        if res.status_code == 200:
            return res.text
        else:
            Log.Error(self, f"Failed to GET {url} (HTTP {res.status_code})")

    def ReadFile(self, filename: str, extension: str, directory: str = ""):
        """
        Read and return the contents of the specified file.

        Optionally specify a relative directory.
        """

        try:
            with open(
                f"{directory}{filename}.{extension}", "r", encoding="utf-8"
            ) as file:
                return file.read()
        except Exception as e:
            Log.Error(self, f"Failed to read {filename}.{extension}, {e}")

    def WriteFile(
        self, filename: str, extension: str, data: str, directory: str = "data/"
    ):
        """
        Write the provided data to the specified file.
        
        Optionally specify a relative directory, defaults to `data/`.
        """

        try:
            with open(
                f"{directory}{filename}.{extension}", "w", encoding="utf-8"
            ) as file:
                file.write(data)
        except Exception as e:
            Log.Error(self, f"Failed to write {filename}.{extension}, {e}")


class ImageUtil:
    """Class containing utilitarian image-based functions intended to reduce duplicate code."""

    def Open(self, filename: str, directory: str = "assets/images/"):
        """Return the specified image file."""

        return Image.open(f"{directory}{filename}")

    def Download(self, url: str):
        """Download and return the raw file from the specified url as an image object."""

        res = requests.get(url, stream=True)

        # HTTP 200 (OK)
        if res.status_code == 200:
            return Image.open(res.raw)
        else:
            Log.Error(self, f"Failed to GET {url} (HTTP {res.status_code})")

    def RatioResize(self, image: Image.Image, maxWidth: int, maxHeight: int):
        """Resize and return the provided image while maintaining aspect ratio."""

        ratio = max(maxWidth / image.width, maxHeight / image.height)

        return image.resize(
            (int(image.width * ratio), int(image.height * ratio)), Image.ANTIALIAS
        )

    def CenterX(self, foregroundWidth: int, backgroundWidth: int, distanceTop: int = 0):
        """Return the tuple necessary for horizontal centering and an optional vertical distance."""

        return (int(backgroundWidth / 2) - int(foregroundWidth / 2), distanceTop)

    def CenterXY(
        self,
        foregroundWidth: int,
        backgroundWidth: int,
        foregroundHeight: int,
        backgroundHeight: int,
    ):
        """Return the tuple necessary for horizontal and vertical centering."""

        return (
            int(backgroundWidth / 2) - int(foregroundWidth / 2),
            int(backgroundHeight / 2) - int(foregroundHeight / 2),
        )
