import json
import logging
import os
from sys import exit

import coloredlogs
import twitter

from util import Utility

log = logging.getLogger(__name__)
coloredlogs.install(level="INFO", fmt="[%(asctime)s] %(message)s", datefmt="%I:%M:%S")


class Sleuth:
    """Fortnite News Feed watcher."""

    def main(self):
        print("Sleuth - Fortnite News Feed watcher")
        print("https://github.com/EthanC/Sleuth\n")

        initialized = Sleuth.LoadConfiguration(self)

        if initialized is True:
            news = Utility.GET(
                self,
                "https://fortnite-api.com/news",
                {"x-api-key": self.apiKey},
                {"language": self.language},
            )

            if news is not None:
                news = json.loads(news)["data"]

                log.info("Retrieved the current news feed")

                # Save The World still uses the messages key, which is
                # not supported in Sleuth at this time.
                # if self.saveTheWorld is True:
                #     Sleuth.Diff(self, "saveTheWorld", news["stw"]["motds"])

                if self.battleRoyale is True:
                    Sleuth.Diff(self, "battleRoyale", news["br"]["motds"])

                if self.creative is True:
                    Sleuth.Diff(self, "creative", news["creative"]["motds"])

    def LoadConfiguration(self):
        """
        Set the configuration values specified in configuration.json
        
        Return True if configuration sucessfully loaded.
        """

        configuration = json.loads(Utility.ReadFile(self, "configuration", "json"))

        try:
            # self.saveTheWorld = configuration["saveTheWorld"]
            self.battleRoyale = configuration["battleRoyale"]
            self.creative = configuration["creative"]
            self.language = configuration["language"]
            self.apiKey = configuration["fortniteAPI"]["apiKey"]
            self.twitterEnabled = configuration["twitter"]["enabled"]
            self.twitterAPIKey = configuration["twitter"]["apiKey"]
            self.twitterAPISecret = configuration["twitter"]["apiSecret"]
            self.twitterAccessToken = configuration["twitter"]["accessToken"]
            self.twitterAccessSecret = configuration["twitter"]["accessSecret"]
            self.hashtags = configuration["hashtags"]
            self.ignoredTitles = configuration["ignoredTitles"]

            log.info("Loaded configuration")

            return True
        except Exception as e:
            log.critical(f"Failed to load configuration, {e}")

    def Diff(self, mode: str, newData: list):
        """
        Determine changes between local and remote news feeds, generate
        a Tweet for any new items.
        """

        if os.path.isfile(f"{mode}.json") is False:
            Utility.WriteFile(self, mode, "json", json.dumps(newData, indent=4))
            log.info(f"Created {mode}.json")

            return

        oldData = json.loads(Utility.ReadFile(self, mode, "json"))
        oldMotds = []
        changed = False

        for motd in oldData:
            if motd.get("id") is not None:
                oldMotds.append(motd.get("id"))

        for motd in newData:
            if (
                (motd.get("id") is not None)
                and (motd.get("id") not in oldMotds)
                and (motd.get("title") not in self.ignoredTitles)
            ):
                body = f"{motd['title']}\n{motd['body']}"

                for hashtag in self.hashtags:
                    # This allows for multi-word strings to be hashtagged
                    hashtagged = hashtag.replace(" ", "")
                    body = body.replace(hashtag, f"#{hashtagged}", 1)

                # Trim Tweet body to <280 characters (275 plus ellipses), as per
                # Twitter's requirements.
                body = body[:275] + (body[275:] and "...")

                log.info(body.replace("\n", " | "))

                if self.twitterEnabled is True:
                    Sleuth.Tweet(self, body, motd["image"])

                changed = True

        if changed is True:
            Utility.WriteFile(self, mode, "json", json.dumps(newData, indent=4))
            log.info(f"Saved {mode}.json")

    def Tweet(self, body: str, imageUrl: str):
        """
        Tweet the provided data to Twitter using the credentials provided
        in `configuration.json`.
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
            log.critical(f"Failed to authenticate with Twitter, {e}")

            return

        try:
            twitterAPI.PostUpdate(body, media=imageUrl)
        except Exception as e:
            log.critical(f"Failed to Tweet news feed, {e}")


if __name__ == "__main__":
    try:
        Sleuth.main(Sleuth)
    except KeyboardInterrupt:
        log.info("Exiting...")
        exit()
