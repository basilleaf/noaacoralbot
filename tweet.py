# -*- coding: utf-8 -*-
import os, random, csv, urllib, logging, StringIO
import PIL.Image as PIL
import tweepy
from resize import shrink
from secrets import CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

# file names
base_path = '/home/befoream/noaacoralbot/'
tweeted_log = base_path + 'tweeted.log'
all_images_csv = base_path + 'scrapings.csv'
max_img_file_size = 3e+6  # 3 megabytes twitter limit

def fetch_image(url):
    """ fetches remote image, returns full path local copy """
    local_img_file = url.split('/')[-1]
    urllib.urlretrieve(url, local_img_file)
    img_path = os.path.abspath(local_img_file)
    return img_path

# pick an emoji
emoji_dividers = ["🐠" ,"🐟" , "🐡", "🐙", "🐚"]
random.shuffle(emoji_dividers)
divider = emoji_dividers[0]

# twitter auth stuff
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth)

# find ones we haven't tweeted yet, handle if none left
all_images = list(open(all_images_csv))  # small data
tweeted = list(open(tweeted_log))
not_yet_tweeted = [line for line in all_images if line not in tweeted]

if not not_yet_tweeted:
    # we've tweeted them all! reset the tweeted.log back to zero
    open(tweeted_log, 'w').close()

# pick a random line from the not_yet_tweeted list
image_info = random.choice(not_yet_tweeted).split(',')
logger.debug(image_info)
(img_id, title, credit, detail_url, hi_res, modest) = [f.strip() for f in image_info]

# trim credit a bit
credit = credit.replace('The Photo Collection of ','')
credit = credit.replace('Photo Collection of ','')

# download image locally
img_path = fetch_image(hi_res)
if max_img_file_size < os.path.getsize(img_path):  # img file too big
    img_path = shrink(img_path, max_img_file_size)
    logger.error("image resized: %s" % img_path)

# compose tweet
tweet = "%s %s %s" % (title, divider, credit)
# is tweet too long? if so then trim title:
title_len_max = 140 - len(divider) - 23 - len(credit) - 2  # title has a max length
                                            # twitter's 140 minus 23 (for link)
                                            # len(divider) (title/credit divider)
                                            # and preserve credit in full
                                            # - 2 for the 2 spaces
if len(tweet) > title_len_max:
    # trim title, -2 for the ellipses, split on words not letters
    trimmed_title = ' '.join(title[0:title_len_max-2].split(' ')[0:-1])
    tweet = "%s.. %s %s" % (trimmed_title, divider, credit)

tweet_with_link = "%s %s" % (tweet, detail_url)

# tweet!
api.update_with_media(img_path, status=tweet_with_link)
logger.info("tweeted %s" % (tweet_with_link))

# add to tweeted.log
with open(tweeted_log, 'a') as csvfile:
    csv_writer = csv.writer(csvfile)
    csv_writer.writerow(list(image_info))

# remove local image
os.remove(img_path)
