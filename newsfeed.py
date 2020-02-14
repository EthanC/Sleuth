import logging
import os
from sys import exit
from typing import Any, List, Optional, Union

import coloredlogs
import twitter

from util import Utility

log: logging.Logger = logging.getLogger(__name__)
coloredlogs.install(level="INFO", fmt="[%(asctime)s] %(message)s", datefmt="%I:%M:%S")


class Sleuth:
    """
    Utility which watches the Fortnite News Feed for changes then
    shares it on Twitter.
    """

    def main(self: Any):
        print("Sleuth - Fortnite News Feed watcher")
        print("https://github.com/EthanC/Sleuth\n")

        initialized: Optional[bool] = Sleuth.LoadConfiguration(self)

        if initialized is True:
            news: Optional[dict] = Utility.GET(
                self,
                "https://fortnite-api.com/news",
                {"x-api-key": self.apiKey},
                {"language": self.language},
            )

            if news is not None:
                log.info("Retrieved the current news feed")

                # Save The World still uses the messages key, which is
                # not supported in Sleuth at this time.
                # if self.saveTheWorld is True:
                #     Sleuth.Diff(self, "saveTheWorld", news["data"]["stw"]["motds"])

                if self.battleRoyale is True:
                    Sleuth.Diff(self, "battleRoyale", news["data"]["br"]["motds"])

                if self.creative is True:
                    Sleuth.Diff(self, "creative", news["data"]["creative"]["motds"])

    def LoadConfiguration(self: Any) -> Optional[bool]:
        """
        Set the configuration values specified in configuration.json
        
        Return True if configuration sucessfully loaded.
        """

        configuration: Optional[Union[dict, str]] = Utility.ReadFile(
            self, "configuration", "json"
        )

        try:
            # self.saveTheWorld: bool = configuration["saveTheWorld"]
            self.battleRoyale: bool = configuration["battleRoyale"]
            self.creative: bool = configuration["creative"]
            self.language: str = configuration["language"]
            self.apiKey: str = configuration["fortniteAPI"]["apiKey"]
            self.twitterEnabled: bool = configuration["twitter"]["enabled"]
            self.twitterAPIKey: str = configuration["twitter"]["apiKey"]
            self.twitterAPISecret: str = configuration["twitter"]["apiSecret"]
            self.twitterAccessToken: str = configuration["twitter"]["accessToken"]
            self.twitterAccessSecret: str = configuration["twitter"]["accessSecret"]
            self.hashtags: List[str] = configuration["hashtags"]
            self.ignoredTitles: List[str] = configuration["ignoredTitles"]
            self.ignoredBodies: List[str] = configuration["ignoredBodies"]

            log.info("Loaded configuration")

            return True
        except Exception as e:
            log.critical(f"Failed to load configuration, {e}")

    def Diff(self: Any, mode: str, newData: List[dict]):
        """
        Determine changes between local and remote news feeds, generate
        a Tweet for any new items.
        """

        if os.path.isfile(f"{mode}.json") is False:
            Utility.WriteFile(self, mode, "json", newData)

            log.info(f"Created {mode}.json")

            return

        oldData: Optional[dict] = Utility.ReadFile(self, mode, "json")
        oldMotds: List[Optional[str]] = []
        changed: bool = False

        motd: dict
        for motd in oldData:
            if motd.get("id") is not None:
                oldMotds.append(motd.get("id"))

        for motd in newData:
            if motd.get("id") in oldMotds:
                continue
            elif motd.get("id") is None:
                continue
            elif (_title := motd.get("title")) in self.ignoredTitles:
                log.info(
                    f'Ignoring news feed item "{_title}" due to ignored title configuration'
                )

                continue
            else:
                for _body in self.ignoredBodies:
                    if _body.lower() in motd["body"].lower():
                        log.info(
                            f'Ignoring news feed item "{_title}" due to ignored body configuration'
                        )

                        return

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
            Utility.WriteFile(self, mode, "json", newData)

            log.info(f"Saved {mode}.json")

    def Tweet(self: Any, body: str, imageUrl: str):
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
        exit()
