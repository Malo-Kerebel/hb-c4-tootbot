# This bot for which I haven't found a name yet

This is a Python bot that looks up posts from specified subreddits and automatically posts them on Twitter. It is based on [tootbot](https://github.com/corbindavenport/tootbot) which is based on [reddit-twitter-bot](https://github.com/rhiever/reddit-twitter-bot). This bot diverges from tootbot by adding the features to wish an happy birthday to people who sign up to it and the ability to play connact 4 with friends

**Features:**

* This bot can post to both Twitter
* Media from direct links, Gfycat, Imgur, Reddit, and Giphy is automatically attached in the social media post
* Links that do not contain media can be skipped, ideal for meme accounts like [@badreactiongifs](https://twitter.com/badreactiongifs)
* NSFW content, spoilers, and self-posts can be filtered
* Tootbot can monitor multiple subreddits at once
* Tootbot is fully open-source, so you don't have to give an external service full access to your social media accounts
* This bot can wish an happy birthday to people that opt in
* This bot allow people to play connect 4

This bot uses the [tweepy](https://github.com/tweepy/tweepy), [PRAW](https://praw.readthedocs.io/en/latest/), [py-gfycat](https://github.com/ankeshanand/py-gfycat), [imgurpython](https://github.com/Imgur/imgurpython), [Pillow](https://github.com/python-pillow/Pillow) and [numpy](https://github.com/numpy/numpy) libraries.

## Disclaimer

The developers of this bot hold no liability for what you do with this script or what happens to you by using this script. Abusing this script *can* get you banned from Twitter, so make sure to read up on proper usage of the API for each site.

## Setup and usage

This bot being really close from tootbot the instruction to set it up are really close from what you can find on [the tootbot wiki](https://github.com/corbindavenport/tootbot/wiki) main difference is that you have to allow your bot to read direct messages for it to work.
