import json
import tweepy
import time
import os
import csv
import configparser
import urllib.parse
import sys
from imgurpython import ImgurClient
from glob import glob
import distutils.core
import itertools
from mastodon import Mastodon
from getmedia import get_media
from getmedia import get_hd_media
from datetime import datetime
import numpy as np
import birthday
import connect4
import report

from main import get_submissions, submission_info


def get_reddit_posts(subreddit_info):
    post_dict = {}
    print('[ OK ] Getting posts from Reddit...')
    for submission in subreddit_info.hot(limit=POST_LIMIT):
        if (submission.over_18 and NSFW_POSTS_ALLOWED is False):
            # Skip over NSFW posts if they are disabled in the config file
            print('[ OK ] Skipping', submission.id, 'because it is marked as NSFW')
            continue
        elif (submission.is_self and SELF_POSTS_ALLOWED is False):
            # Skip over NSFW posts if they are disabled in the config file
            print('[ OK ] Skipping', submission.id, 'because it is a self post')
            continue
        elif (submission.spoiler and SPOILERS_ALLOWED is False):
            # Skip over posts marked as spoilers if they are disabled in the config file
            print('[ OK ] Skipping', submission.id, 'because it is marked as a spoiler')
            continue
        elif (submission.stickied):
            print('[ OK ] Skipping', submission.id, 'because it is stickied')
            continue
        else:
            # Create dict
            post_dict[submission.id] = submission
    return post_dict


def get_caption(submission, max_length):
    # Create string of hashtags
    flair = ""
    hashtag_string = ''
    #if (str(submission.link_flair_text) != "None" and FLAIR_ALLOWED):
    #    flair = str(submission.link_flair_text) + ' '

    url = f"https://raddle.me/f/{FORUM_TO_MONITOR}/{submission['id']}"

    if HASHTAGS:
        for x in HASHTAGS:
            # Add hashtag to string, followed by a space for the next one
            hashtag_string += '#' + x + ' '
    # Set the Mastodon max title length for 500, minus the length of the shortlink and hashtags, minus one for the space between title and shortlink
    max_title_length = max_length - len(flair) - len(url) - len(hashtag_string) - 1
    # Create contents of the Mastodon post
    if len(submission["title"]) < max_length:
        mastodon_caption = submission["title"] + ' ' + flair + hashtag_string + url
    else:
        mastodon_caption = submission["title"][:max_title_length] + '... ' + hashtag_string + url
    return mastodon_caption, flair


def duplicate_check(id):
    value = False
    with open(CACHE_CSV, 'rt', newline='') as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            if id in row:
                value = True
    f.close()
    return value


def log_post(id, post_url):
    with open(CACHE_CSV, 'a', newline='') as cache:
        date = time.strftime("%d/%m/%Y") + ' ' + time.strftime("%H:%M:%S")
        wr = csv.writer(cache, delimiter=',')
        wr.writerow([id, date, post_url])
    cache.close()


def deleteLine(myfile, st):
    f = open(myfile)
    output = []
    for line in f:
        if not line.startswith(st):
            output.append(line)
    f.close()
    f = open(myfile, 'w')
    f.writelines(output)
    f.close()


def hour():

    now = datetime.now()
    hour = str(now.hour) + ':' + str(now.minute)

    return hour


def check_messages():

    arrayMessage = twitter.get_direct_messages()
    done = open("done.txt", 'r')
    data = done.readlines()
    arrayMessage = [messages for messages in arrayMessage if messages.message_create["target"]["recipient_id"] == str(twitter.verify_credentials().id) and int(messages.id) > int(data[1])]
    print("[ OK ] " + str(len(arrayMessage)) + " message to process")
    # print(arrayMessage)
    for message in reversed(arrayMessage):
        check_message(message)


def check_message(message):

    textMessage = message.message_create["message_data"]["text"]
    arrayMessage = textMessage.split()
    userID = message.message_create["sender_id"]
    done = open("done.txt", 'r')
    data = done.readlines()

    if (data[1] < message.id):
        deleteLine("done.txt", data[1])
        done.close()
        done = open("done.txt", 'a')
        done.write(message.id)
        # Change the id in the done.txt file so that the bot doesn't process the same message twice

        # Big elif because I don't know how to do it better
        if (textMessage[0] == '/'):
            if (arrayMessage[0] == "/connect4" or arrayMessage[0] == "/c4"):
                connect4.main(arrayMessage, userID, twitter)
            elif (arrayMessage[0] == "/birthday" or arrayMessage[0] == "/bd"):
                birthday.main(arrayMessage, userID, twitter)
            elif (arrayMessage[0] == "/help" or arrayMessage[0] == "/h"):
                twitter.send_direct_message(userID, "There are currently 4 commands available :\n\n/connect4 (or /c4) that allows you to play a connect4 game with a friend, use /connect4 -help to get more information about this command\n\n/birthday (or /bd) that allows you to register so that the bot wishes you an happy birthday, use /birthday -help to get more information about this command\n\n/report (or /r) send a report to the account owner for further inspection and potentially delete the tweet, use /report -help to get more information about this command\n\n/help (or -h) that displays this message")
            elif (arrayMessage[0] == "/report" or arrayMessage[0] == "/r"):
                if (TWITTER_OWNER != ""):
                    report.main(textMessage, arrayMessage, userID, twitter, TWITTER_OWNER)
                else:
                    twitter.send_direct_message(userID, "The report command has been disabled")
            elif (arrayMessage[0] == "/delete" or arrayMessage[0] == "/d"):
                if (userID == TWITTER_OWNER):
                    if (len(arrayMessage) > 1):
                        report.delete(arrayMessage[1], twitter)
                    else:
                        twitter.send_direct_message(userID, "You must enter an ID")
                else:
                    twitter.send_direct_message(userID, "Only the administrator has access to this command")
            elif (arrayMessage[0] == "/spare" or arrayMessage[0] == "/s"):
                if (userID == TWITTER_OWNER):
                    if (len(arrayMessage) > 1):
                        report.reject(arrayMessage[1], twitter)
                    else:
                        twitter.send_direct_message(userID, "You must enter an ID")
                else:
                    twitter.send_direct_message(userID, "Only the administrator has access to this command")
            else:
                twitter.send_direct_message(userID, "This command doesn't exist, use /help to get a list of the different commands available\n\nIf you still don't understand how to use the command contact @Mahkda_ directly")


def make_post(ids, urls, FLAIR_ALLOWED):
    for i in range(len(ids)):
        # Get the info for the specific id
        id = ids[i]
        url = urls[i]
        post = submission_info(FORUM_TO_MONITOR, id)
        if not duplicate_check(id):  # Make sure post is not a duplicate
            media_file = get_hd_media(url, IMGUR_CLIENT, IMGUR_CLIENT_SECRET)
            # Post on Twitter
            if POST_TO_TWITTER:
                if (((MEDIA_POSTS_ONLY is True) and media_file) or (MEDIA_POSTS_ONLY is False)):

                    try:
                        auth = tweepy.OAuthHandler(
                            CONSUMER_KEY, CONSUMER_SECRET)
                        auth.set_access_token(
                            ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
                        twitterv1 = tweepy.API(auth)
                        # Generate post caption
                        caption, flair = get_caption(post, 280)
                        # Post the tweet
                        if (media_file):
                            if type(media_file) is list:
                                media_ids = [twitterv1.media_upload(i).media_id_string for i in media_file[:4]]
                                print('[ OK ] Posting first tweet on Twitter with media attachment:', caption)
                                if "phobia" in caption:
                                    tweet = twitter.create_tweet(text=caption, media_ids=media_ids, possibly_sensitive=True)
                                else:
                                    tweet = twitter.create_tweet(text=caption, media_ids=media_ids)
                                if len(media_file) > 4:
                                    media_ids = [twitterv1.media_upload(i).media_id_string for i in media_file[4:8]]
                                    print('[ OK ] Posting second tweet on Twitter with media attachment:', caption)
                                    if "phobia" in caption:
                                            tweet = twitter.create_tweet(text=caption, in_reply_to_status_id=str(tweet.id), media_ids=media_ids, possibly_sensitive=True)
                                    else:
                                            tweet = twitter.create_tweet(text=caption, in_reply_to_status_id=str(tweet.id), media_ids=media_ids)
                                if len(media_file) > 8:
                                    media_ids = [twitterv1.media_upload(i).media_id_string for i in media_file[8:12]]
                                    print('[ OK ] Posting third tweet on Twitter with media attachment:', caption)
                                    if "phobia" in caption:
                                            tweet = twitter.create_tweet(text=caption, in_reply_to_status_id=str(tweet.id), media_ids=media_ids, possibly_sensitive=True)
                                    else:
                                            tweet = twitter.create_tweet(text=caption, in_reply_to_status_id=str(tweet.id), media_ids=media_ids)
                                if len(media_file) > 12:
                                    media_ids = [twitterv1.media_upload(i).media_id_string for i in media_file[12:16]]
                                    print('[ OK ] Posting fourth tweet on Twitter with media attachment:', caption)
                                    if "phobia" in caption:
                                            tweet = twitter.create_tweet(text=caption, in_reply_to_status_id=str(tweet.id), media_ids=media_ids, possibly_sensitive=True)
                                    else:
                                            tweet = twitter.create_tweet(text=caption, in_reply_to_status_id=str(tweet.id), media_ids=media_ids)
                                if len(media_file) > 16:
                                    media_ids = [twitterv1.media_upload(i).media_id_string for i in media_file[16:20]]
                                    print('[ OK ] Posting fifth tweet on Twitter with media attachment:', caption)
                                    if "phobia" in caption:
                                            tweet = twitter.create_tweet(text=caption, in_reply_to_status_id=str(tweet.id), media_ids=media_ids, possibly_sensitive=True)
                                    else:
                                            tweet = twitter.create_tweet(text=caption, in_reply_to_status_id=str(tweet.id), media_ids=media_ids)
                                    # We can't have more than 20 images in a reddit gallery
                            else:
                                if "phobia" in caption:
                                    media_id = [twitterv1.media_upload(media_file).media_id_string]
                                    tweet = twitter.create_tweet(text=caption, media_ids=media_id, possibly_sensitive=True)
                                else:
                                    media_id = [twitterv1.media_upload(media_file).media_id_string]
                                    tweet = twitter.create_tweet(text=caption, media_ids=media_id)
                            print('[ OK ] Posting this on Twitter with media attachment:', caption)

                            if not MASTODON_INSTANCE_DOMAIN:
                                # Clean up media file
                                try:

                                    os.remove(media_file)
                                    print('[ OK ] Deleted media file at', media_file)
                                except BaseException as e:
                                    print('[EROR] Error while deleting media file:', str(e))
                        else:
                            print('[ OK ] Posting this on Twitter:', caption)
                            tweet = twitter.create_tweet(text=caption)
                        # Log the tweet
                        if not MASTODON_INSTANCE_DOMAIN:
                            log_post(id, 'https://twitter.com/' + twitter_username + '/status/' + tweet.id_str + '/')
                    except BaseException as e:
                        print('[EROR] Error while posting tweet:', str(e))
                        # Log the post anyways
                        log_post(id, 'Error while posting tweet: ' + str(e))
                else:
                    print('[WARN] Twitter: Skipping', id, 'because non-media posts are disabled or the media file was not found')
                    # Log the post anyways
                    log_post(id, 'Twitter: Skipped because non-media posts are disabled or the media file was not found')

            # Post on Mastodon
            if MASTODON_INSTANCE_DOMAIN:
                # Make sure the post contains media, if MEDIA_POSTS_ONLY in config is set to True
                if (((MEDIA_POSTS_ONLY is True) and media_file) or (MEDIA_POSTS_ONLY is False)):
                    try:
                        # Generate post caption
                        caption, flair = get_caption(post, 500)
                        print(f"caption : {caption}")
                        print(f"flair : {flair}")
                        # Post the toot
                        if (media_file):
                            print(
                                '[ OK ] Posting this on Mastodon with media attachment:', caption)
                            media = mastodon.media_post(media_file, mime_type=None)
                            # If the post is marked as NSFW on Reddit, force sensitive media warning for images
                            if len(flair) > 0:
                                toot = mastodon.status_post(caption, media_ids=[media], spoiler_text=flair)
                            else:
                                toot = mastodon.status_post(caption, media_ids=[media], sensitive=MASTODON_SENSITIVE_MEDIA)
                            # Clean up media file
                            try:
                                os.remove(media_file)
                                print('[ OK ] Deleted media file at', media_file)
                            except BaseException as e:
                                print('[EROR] Error while deleting media file:', str(e))
                        else:
                            print('[ OK ] Posting this on Mastodon:', caption)
                            # Add NSFW warning for Reddit posts marked as NSFW
                            if (post_dict[post].over_18 == True):
                                toot = mastodon.status_post(caption, spoiler_text='NSFW')
                            else:
                                toot = mastodon.status_post(caption)
                        # Log the toot
                        log_post(id, toot["url"])
                    except BaseException as e:
                        print('[EROR] Error while posting toot:', str(e))
                        # Log the post anyways
                        log_post(id, 'Error while posting toot: ' + str(e))
                else:
                    print('[WARN] Mastodon: Skipping', id, 'because non-media posts are disabled or the media file was not found')
                    # Log the post anyways
                    log_post(id, 'Mastodon: Skipped because non-media posts are disabled or the media file was not found')
            break
        else:
            print('[ OK ] Skipping', id, 'because it was already posted')


# Make sure config file exists
try:
    config = configparser.ConfigParser()
    config.read('config.ini')
except BaseException as e:
    print('[EROR] Error while reading config file:', str(e))
    sys.exit()
# General settings
CACHE_CSV = config['BotSettings']['CacheFile']
DELAY_BETWEEN_TWEETS = int(config['BotSettings']['DelayBetweenPosts'])
POST_LIMIT = int(config['BotSettings']['PostLimit'])
SUBREDDIT_TO_MONITOR = config['BotSettings']['SubredditToMonitor']
FORUM_TO_MONITOR = config['BotSettings']['ForumToMonitor']
NSFW_POSTS_ALLOWED = bool(distutils.util.strtobool(
    config['BotSettings']['NSFWPostsAllowed']))
SPOILERS_ALLOWED = bool(distutils.util.strtobool(
    config['BotSettings']['SpoilersAllowed']))
SELF_POSTS_ALLOWED = bool(distutils.util.strtobool(
    config['BotSettings']['SelfPostsAllowed']))
if config['BotSettings']['Hashtags']:
    # Parse list of hashtags
    HASHTAGS = config['BotSettings']['Hashtags']
    HASHTAGS = [x.strip() for x in HASHTAGS.split(',')]
else:
    HASHTAGS = ''
FLAIR_ALLOWED = bool(distutils.util.strtobool(
    config['BotSettings']['Flair']))
# Settings related to media attachments
MEDIA_POSTS_ONLY = bool(distutils.util.strtobool(
    config['MediaSettings']['MediaPostsOnly']))
# Twitter info
POST_TO_TWITTER = bool(distutils.util.strtobool(
    config['Twitter']['PostToTwitter']))
TWITTER_OWNER = config['Twitter']['TwitterOwner']
# Mastodon info
MASTODON_INSTANCE_DOMAIN = config['Mastodon']['InstanceDomain']
MASTODON_SENSITIVE_MEDIA = bool(
    distutils.util.strtobool(config['Mastodon']['SensitiveMedia']))
# Setup and verify Reddit access
if not os.path.exists('reddit.secret'):
    print('[WARN] API keys for Reddit not found. Please enter them below (see wiki if you need help).')
    # Whitespaces are stripped from input: https://stackoverflow.com/a/3739939
    REDDIT_AGENT = ''.join(input("[ .. ] Enter Reddit agent: ").split())
    REDDIT_CLIENT_SECRET = ''.join(
        input("[ .. ] Enter Reddit client secret: ").split())
    # Make sure authentication is working
    try:
        reddit_client = praw.Reddit(
            user_agent='Tootbot', client_id=REDDIT_AGENT, client_secret=REDDIT_CLIENT_SECRET)
        test = reddit_client.subreddit('announcements')
        # It worked, so save the keys to a file
        reddit_config = configparser.ConfigParser()
        reddit_config['Reddit'] = {
            'Agent': REDDIT_AGENT,
            'ClientSecret': REDDIT_CLIENT_SECRET
        }
        with open('reddit.secret', 'w') as f:
            reddit_config.write(f)
        f.close()
    except BaseException as e:
        print('[EROR] Error while logging into Reddit:', str(e))
        print('[EROR] Tootbot cannot continue, now shutting down')
        exit()
else:
    # Read API keys from secret file
    reddit_config = configparser.ConfigParser()
    reddit_config.read('reddit.secret')
    REDDIT_AGENT = reddit_config['Reddit']['Agent']
    REDDIT_CLIENT_SECRET = reddit_config['Reddit']['ClientSecret']

# Setup and verify Imgur access
if not os.path.exists('imgur.secret'):
    print('[WARN] API keys for Imgur not found. Please enter them below (see wiki if you need help).')
    # Whitespaces are stripped from input: https://stackoverflow.com/a/3739939
    IMGUR_CLIENT = ''.join(input("[ .. ] Enter Imgur client ID: ").split())
    IMGUR_CLIENT_SECRET = ''.join(
        input("[ .. ] Enter Imgur client secret: ").split())
    # Make sure authentication is working
    try:
        imgur_client = ImgurClient(IMGUR_CLIENT, IMGUR_CLIENT_SECRET)
        test_gallery = imgur_client.get_album('dqOyj')
        # It worked, so save the keys to a file
        imgur_config = configparser.ConfigParser()
        imgur_config['Imgur'] = {
            'ClientID': IMGUR_CLIENT,
            'ClientSecret': IMGUR_CLIENT_SECRET
        }
        with open('imgur.secret', 'w') as f:
            imgur_config.write(f)
        f.close()
    except BaseException as e:
        print('[EROR] Error while logging into Imgur:', str(e))
        print('[EROR] Tootbot cannot continue, now shutting down')
        exit()
else:
    # Read API keys from secret file
    imgur_config = configparser.ConfigParser()
    imgur_config.read('imgur.secret')
    IMGUR_CLIENT = imgur_config['Imgur']['ClientID']
    IMGUR_CLIENT_SECRET = imgur_config['Imgur']['ClientSecret']


# Log into Twitter if enabled in settings
if POST_TO_TWITTER is True:
    if os.path.exists('twitter.secret'):
        # Read API keys from secret file
        twitter_config = configparser.ConfigParser()
        twitter_config.read('twitter.secret')
        ACCESS_TOKEN = twitter_config['Twitter']['AccessToken']
        ACCESS_TOKEN_SECRET = twitter_config['Twitter']['AccessTokenSecret']
        CONSUMER_KEY = twitter_config['Twitter']['ConsumerKey']
        CONSUMER_SECRET = twitter_config['Twitter']['ConsumerSecret']
        #BEARER_TOKEN = twitter_config['Twitter']['bearertoken']
        BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAABM0%2FgAAAAAAso6Uix3X4hakA3k8L9349qHbFUs%3Deq0Llc8I69iiOWNiW4JGiJ5NdNnKDbpTSVUNAgkExZaF1ZTF3t"
        try:
            # Make sure authentication is working
            twitter = tweepy.Client(BEARER_TOKEN, CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET, wait_on_rate_limit=True)
            twitter_username = twitter.get_me()[0]
            print('[ OK ] Sucessfully authenticated on Twitter as @' +
                  str(twitter_username))
        except BaseException as e:
            print('[EROR] Error while logging into Twitter:', str(e))
            print('[EROR] Tootbot cannot continue, now shutting down')
            exit()
    else:
        # If the secret file doesn't exist, it means the setup process hasn't happened yet
        print('[WARN] API keys for Twitter not found. Please enter them below (see wiki if you need help).')
        # Whitespaces are stripped from input: https://stackoverflow.com/a/3739939
        ACCESS_TOKEN = ''.join(
            input('[ .. ] Enter access token for Twitter account: ').split())
        ACCESS_TOKEN_SECRET = ''.join(
            input('[ .. ] Enter access token secret for Twitter account: ').split())
        CONSUMER_KEY = ''.join(
            input('[ .. ] Enter consumer key for Twitter account: ').split())
        CONSUMER_SECRET = ''.join(
            input('[ .. ] Enter consumer secret for Twitter account: ').split())
        print('[ OK ] Attempting to log in to Twitter...')
        try:
            # Make sure authentication is working
            auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
            auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
            twitter = tweepy.API(auth)
            twitter_username = twitter.verify_credentials().screen_name
            print('[ OK ] Sucessfully authenticated on Twitter as @' +
                  twitter_username)
            # It worked, so save the keys to a file
            twitter_config = configparser.ConfigParser()
            twitter_config['Twitter'] = {
                'AccessToken': ACCESS_TOKEN,
                'AccessTokenSecret': ACCESS_TOKEN_SECRET,
                'ConsumerKey': CONSUMER_KEY,
                'ConsumerSecret': CONSUMER_SECRET
            }
            with open('twitter.secret', 'w') as f:
                twitter_config.write(f)
            f.close()
        except BaseException as e:
            print('[EROR] Error while logging into Twitter:', str(e))
            print('[EROR] Tootbot cannot continue, now shutting down')
            exit()


# Log into Mastodon if enabled in settings
if MASTODON_INSTANCE_DOMAIN:
    if not os.path.exists('mastodon.secret'):
        # If the secret file doesn't exist, it means the setup process hasn't happened yet
        print('[WARN] API keys for Mastodon not found. Please enter them below (see wiki if you need help).')
        MASTODON_USERNAME = input(
            "[ .. ] Enter email address for Mastodon account: ")
        MASTODON_PASSWORD = input(
            "[ .. ] Enter password for Mastodon account: ")
        print('[ OK ] Generating login key for Mastodon...')
        try:
            Mastodon.create_app(
                'Tootbot',
                website='https://github.com/corbindavenport/tootbot',
                api_base_url='https://' + MASTODON_INSTANCE_DOMAIN,
                to_file='mastodon.secret'
            )
            mastodon = Mastodon(
                client_id='mastodon.secret',
                api_base_url='https://' + MASTODON_INSTANCE_DOMAIN
            )
            mastodon.log_in(
                MASTODON_USERNAME,
                MASTODON_PASSWORD,
                to_file='mastodon.secret'
            )
            # Make sure authentication is working
            masto_username = mastodon.account_verify_credentials()['username']
            print('[ OK ] Sucessfully authenticated on ' + MASTODON_INSTANCE_DOMAIN + ' as @' +
                  masto_username + ', login information now stored in mastodon.secret file')
        except BaseException as e:
            print('[EROR] Error while logging into Mastodon:', str(e))
            print('[EROR] Tootbot cannot continue, now shutting down')
            exit()
    else:
        try:
            mastodon = Mastodon(
                access_token='mastodon.secret',
                api_base_url='https://' + MASTODON_INSTANCE_DOMAIN
            )
            # Make sure authentication is working
            username = mastodon.account_verify_credentials()['username']
            print('[ OK ] Sucessfully authenticated on ' +
                  MASTODON_INSTANCE_DOMAIN + ' as @' + username)
        except BaseException as e:
            print('[EROR] Error while logging into Mastodon:', str(e))
            print('[EROR] Tootbot cannot continue, now shutting down')
            exit()
# Set the command line window title on Windows
if (os.name == 'nt'):
    try:
        if POST_TO_TWITTER and MASTODON_INSTANCE_DOMAIN:
            # Set title with both Twitter and Mastodon usernames
            # twitter_username = twitter.verify_credentials().screen_name
            masto_username = mastodon.account_verify_credentials()['username']
            os.system('title ' + twitter_username + '@twitter.com and ' +
                      masto_username + '@' + MASTODON_INSTANCE_DOMAIN + ' - Tootbot')
        elif POST_TO_TWITTER:
            # Set title with just Twitter username
            twitter_username = twitter.verify_credentials().screen_name
            os.system('title ' + '@' + twitter_username + ' - Tootbot')
        elif MASTODON_INSTANCE_DOMAIN:
            # Set title with just Mastodon username
            masto_username = mastodon.account_verify_credentials()['username']
            os.system('title ' + masto_username + '@' +
                      MASTODON_INSTANCE_DOMAIN + ' - Tootbot')
    except:
        os.system('title Tootbot')


# Run the main script
while True:

    # process birthday
    # birthday.check_birthday(twitter, datetime.now())

    # Make sure logging file and media directory exists
    if not os.path.exists(CACHE_CSV):
        with open(CACHE_CSV, 'w', newline='') as cache:
            default = ['Reddit post ID', 'Date and time', 'Post link']
            wr = csv.writer(cache)
            wr.writerow(default)
        print('[ OK ] ' + CACHE_CSV + ' file not found, created a new one')
        cache.close()
    # Continue with script
    try:
        #subreddit = setup_connection_reddit(SUBREDDIT_TO_MONITOR)
        #post_dict = get_reddit_posts(subreddit)
        ids, urls = get_submissions(FORUM_TO_MONITOR)
        make_post(ids, urls, FLAIR_ALLOWED)
    except BaseException as e:
        print(e)
        print('[EROR] Error in main process')

    # Process messages
    for i in range(int(DELAY_BETWEEN_TWEETS//200)):
        try:
            # check_messages()
            pass
        except BaseException as e:
            print("[ ERROR ] Couldn't read messages :", e)
        time.sleep(200)
    print(hour() + '[ OK ] Restarting main process...')
