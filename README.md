# Sleuth

Sleuth is a utility which watches the Fortnite News Feed for changes then generates a stylized image and shares it on Twitter.

As seen on [@FNMasterCom](https://twitter.com/FNMasterCom)...

## Requirements

- [Python3.7](https://www.python.org/downloads/)
- [Requests](http://docs.python-requests.org/en/master/user/install/)
- [Colorama](https://pypi.org/project/colorama/)
- [Pillow](https://pillow.readthedocs.io/en/stable/installation.html#basic-installation)
- [python-twitter](https://github.com/bear/python-twitter#installing)

[Twitter API credentials](https://developer.twitter.com/en/apps) are required to Tweet the image.

## Usage

Open `configuration_example.json` in your preferred text editor, fill the configurable values. Once finished, save and rename the file to `configuration.json`.

- `twitter`: Set `enabled` to `false` if you wish for `news.png` to not be Tweeted

Edit the images found in `assets/images/` to your liking, avoid changing image dimensions for optimal results.

```
python newsfeed.py
```

## Credits

- News Feed data provided by the [Fortnite API](https://fortnitecontent-website-prod07.ol.epicgames.com/content/api/pages/fortnite-game)
