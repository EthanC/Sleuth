import json
import os
from sys import exit

import twitter
from PIL import Image, ImageDraw

from logger import Log
from util import ImageUtil, Utility


class Sleuth:
    """Fortnite News Feed watcher."""

    def main(self):
        Log.Intro(self, "Sleuth - Fortnite News Feed watcher")
        Log.Intro(self, "https://github.com/EthanC/Sleuth\n")

        initialized = Sleuth.LoadConfiguration(self)

        if initialized is True:
            news = Sleuth.GetNews(self)

            if news is not None:
                news = json.loads(news)["battleroyalenews"]["news"]["messages"]

                Log.Success(self, "Retrieved the current Fortnite News Feed")

                if os.path.isfile(f"data/news.json") == False:
                    Log.Info(self, "news.json does not exist, creating it")

                    Utility.WriteFile(self, "news", "json", json.dumps(news))
                else:
                    diff = Sleuth.Diff(self, news)

                    if len(diff) == 0:
                        Log.Info(self, "No changes found in News Feed")
                    else:
                        for item in news:
                            if item["title"] in diff:
                                if self.twitterEnabled is True:
                                    Sleuth.GenerateTweet(self, item)

                        Utility.WriteFile(self, "news", "json", json.dumps(news))

    def LoadConfiguration(self):
        """
        Set the configuration values specified in configuration.json
        
        Return True if configuration sucessfully loaded.
        """

        configuration = json.loads(Utility.ReadFile(self, "configuration", "json"))

        try:
            self.hashtags = configuration["hashtags"]
            self.ignoredTitles = configuration["ignoredTitles"]
            self.twitterEnabled = configuration["twitter"]["enabled"]
            self.twitterAPIKey = configuration["twitter"]["apiKey"]
            self.twitterAPISecret = configuration["twitter"]["apiSecret"]
            self.twitterAccessToken = configuration["twitter"]["accessToken"]
            self.twitterAccessSecret = configuration["twitter"]["accessSecret"]

            Log.Success(self, "Loaded configuration")

            return True
        except Exception as e:
            Log.Error(self, f"Failed to load configuration, {e}")

    def GetNews(self):
        """Return the current News Feed from the Fortnite API."""

        url = "https://fortnitecontent-website-prod07.ol.epicgames.com/content/api/pages/fortnite-game"

        return Utility.GET(self, url)

    def Diff(self, news: list):
        """Return a list of News Feed titles which were not previously present."""

        changed = []
        oldTitles = []

        oldNews = json.loads(Utility.ReadFile(self, "news", "json", "data/"))

        # We're only interested in taking action on entirely new News
        # items, thus we are only comparing titles. This can be easily
        # modified to compare the image, body, and adspace of the items.
        for item in oldNews:
            oldTitles.append(item["title"])

        for item in news:
            if (item["title"] not in oldTitles) and (
                item["title"] not in self.ignoredTitles
            ):
                changed.append(item["title"])

        return changed

    def GenerateTweet(self, item: dict):
        """
        Tweet the current `news.png` local file to Twitter using the credentials provided in `configuration.json`.
        """

        try:
            twitterAPI = twitter.Api(
                consumer_key=self.twitterAPIKey,
                consumer_secret=self.twitterAPISecret,
                access_token_key=self.twitterAccessToken,
                access_token_secret=self.twitterAccessSecret,
            )

            twitterAPI.VerifyCredentials()
        except Exception as e:
            Log.Error(self, f"Failed to authenticate with Twitter, {e}")

            return

        # Not all News Feed items will have the adspace element. If it
        # is present, include it in the Tweet body.
        try:
            adspace = item["adspace"].capitalize()

            # In some cases, the adspace key will be present, however
            # the value will be blank.
            if len(adspace) > 0:
                body = "{} ({})\n{}".format(item["title"], adspace, item["body"])
            else:
                raise KeyError
        except KeyError:
            body = "{}\n{}".format(item["title"], item["body"])

        for hashtag in self.hashtags:
            # This allows for multi-word strings to be hashtagged
            hashtagged = hashtag.replace(" ", "")

            body = body.replace(hashtag, f"#{hashtagged}", 1)

        imageURL = item["image"]
        Sleuth.GenerateImage(self, imageURL)

        # Trim Tweet body to 280 characters (277 plus ellipses), as per
        # Twitter's requirements.
        body = body[:277] + (body[277:] and "...")

        Log.Info(self, f"{body}\n{imageURL}")

        try:
            with open("news.png", "rb") as image:
                twitterAPI.PostUpdate(body, media=image)

            Log.Success(self, "Tweeted News Feed change")
        except Exception as e:
            Log.Error(self, f"Failed to Tweet News Feed change, {e}")

    def GenerateImage(self, url: str):
        """Save a stylized image using the specified News Feed image URL as `news.png`."""

        try:
            card = Image.new("RGBA", (1280, 720))
            background = ImageUtil.Open(self, "background.png")
            logo = ImageUtil.Open(self, "logo.png")
            newsImage = ImageUtil.Download(self, url).convert("RGBA")

            # Images obtained from the Fortnite Battle Royale News API
            # should always be 1024x512. This is simply a precautionary
            # measure to prevent any design issues.
            if (newsImage.width != 1024) or (newsImage.height != 512):
                Log.Warn(self, "Expected image with dimensions 1024x512, resizing")
                newsImage = ImageUtil.RatioResize(self, newsImage, 1024, 512)

            card.paste(background)
            card.paste(
                newsImage,
                ImageUtil.CenterXY(
                    self, newsImage.width, card.width, newsImage.height, card.height
                ),
                newsImage,
            )
            card.paste(logo, ImageUtil.CenterX(self, logo.width, card.width, 575), logo)

            card.save("news.png")
        except Exception as e:
            Log.Error(self, f"Failed to generate image, {e}")


if __name__ == "__main__":
    try:
        Sleuth.main(Sleuth)
    except KeyboardInterrupt:
        Log.Info(Sleuth, "Exiting...")
        exit()
