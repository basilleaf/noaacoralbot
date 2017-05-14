import os, random, csv, urllib
import tweepy
from secrets import CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET

# file names
tweeted_log = 'tweeted.log'
all_images_csv = 'scrapings.csv'

# twitter auth stuff
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth)

# find ones we haven't tweeted yet, handle if none left
all_images = list(open(all_images_csv))
tweeted = list(open(tweeted_log))
not_yet_tweeted = [line for line in all_images if line not in tweeted]

if not not_yet_tweeted:
    # we've tweeted them all! reset the tweeted.log back to zero #todo
    pass

# pick a random line from the not_yet_tweeted list
image_info = random.choice(not_yet_tweeted).split(',')
print image_info
(img_id, title, credit, detail_url, hi_res, modest) = [f.strip() for f in image_info]

# download image locally
local_img_file = modest.split('/')[-1]
urllib.urlretrieve(modest, local_img_file)
img_path = os.path.abspath(local_img_file)

# tweet!
title_len_max = 137 - len(credit)  # trim the title not the credit
                                   # 140-3 = 137, 3 the length of " | "
tweet = "%s | %s" % (title[0:title_len_max], credit)
tweet_with_link = "%s %s" % (tweet, detail_url)
print tweet_with_link
api.update_with_media(img_path, status=tweet_with_link)
print "tweeted %s" % (tweet_with_link)

# add to tweeted.log
with open(tweeted_log, 'a') as csvfile:
    csv_writer = csv.writer(csvfile)
    csv_writer.writerow(image_info)

# remove local image
os.remove(local_img_file)
