import os, random, csv, urllib
import tweepy
from secrets import CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET

import logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

# file names
base_path = '/home/befoream/noaacoralbot/'
tweeted_log = base_path + 'tweeted.log'
all_images_csv = base_path + 'scrapings.csv'

def fetch_image(url):
    """ fetches remote image, returns full path local copy """
    local_img_file = url.split('/')[-1]
    urllib.urlretrieve(url, local_img_file)
    img_path = os.path.abspath(local_img_file)
    return img_path

# twitter auth stuff
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth)

# find ones we haven't tweeted yet, handle if none left
all_images = list(open(all_images_csv))  # small data
tweeted = list(open(tweeted_log))
not_yet_tweeted = [line for line in all_images if line not in tweeted]

if not not_yet_tweeted:
    # we've tweeted them all! reset the tweeted.log back to zero #todo
    pass

# pick a random line from the not_yet_tweeted list
image_info = random.choice(not_yet_tweeted).split(',')
logger.debug(image_info)
(img_id, title, credit, detail_url, hi_res, modest) = [f.strip() for f in image_info]

# download image locally
img_path = fetch_image(hi_res)

# compose tweet
title_len_max = 137 - len(credit)  # trim the title not the credit
                                   # 137 = 140-3, 3 the length of:
                                   # divider between tweet/credit = " | "
tweet = "%s | %s" % (title[0:title_len_max], credit)
tweet_with_link = "%s %s" % (tweet, detail_url)

# tweet!
logger.debug(tweet_with_link)
try:
    api.update_with_media(img_path, status=tweet_with_link)
    print "tweeted %s" % (tweet_with_link)
except e:
    # try the modest size
    print e # coding=utf-8
    print "trying for modest size"
    os.remove(img_path)  # remove the local hi_res
    img_path = fetch_image(modest)
    api.update_with_media(img_path, status=tweet_with_link)
    print "tweeted %s" % (tweet_with_link)

# add to tweeted.log
with open(tweeted_log, 'a') as csvfile:
    csv_writer = csv.writer(csvfile)
    csv_writer.writerow(list(image_info))

# remove local image
os.remove(img_path)
