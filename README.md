# Sleuth

Sleuth is a utility which watches the Fortnite News Feed for changes then shares it on Twitter.

As seen on [@FNMasterCom](https://twitter.com/FNMasterCom/status/1227955872057450497)...

<p align="center">
    <img src="https://i.imgur.com/JIZUwmV.jpg" width="650px" draggable="false">
</p>

## Requirements

-   [Python 3.7](https://www.python.org/downloads/)
-   [httpx](https://www.python-httpx.org/#installation)
-   [coloredlogs](https://pypi.org/project/coloredlogs/)
-   [python-twitter](https://github.com/bear/python-twitter#installing)

A [Fortnite-API API Key](https://fortnite-api.com/profile) is required to obtain the News Feed data, [Twitter API credentials](https://developer.twitter.com/en/apps) are required to Tweet the image.

## Usage

Open `configuration_example.json` in your preferred text editor, fill the configurable values. Once finished, save and rename the file to `configuration.json`.

-   `language`: Set the language for the News Feed data ([Supported Languages](https://fortnite-api.com/documentation))
-   `twitter`: Set `enabled` to `false` if you wish for the news to not be Tweeted
-   `ignoredTitles`: Array of News Feed titles which should not be Tweeted
-   `ignoredBodies`: Array of News Feed bodies which should not be Tweeted
-   `hashtags`: Array of strings which should be converted to hashtags

Sleuth is designed to be ran using a scheduler, such as [cron](https://en.wikipedia.org/wiki/Cron).

```
python newsfeed.py
```

## Credits

-   News Feed data provided by [Fortnite-API](https://fortnite-api.com/)
