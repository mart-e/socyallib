#!/usr/bin/env python

from socyallib import Twitter, StatusNet
import logging
logger = logging.getLogger('socyallib')

print("Twitter")
tw = Twitter(configuration_file="socyallib/config.json")
tw.authenticate(wizard=True)

feed = tw.timeline
for tweet_item in feed:
    tweet = tweet_item.convert('object')
    print("@{0}: {1}".format(tweet.sender, tweet.text))


print("StatusNet")
sn = StatusNet(configuration_file="socyallib/config.json")
sn.authenticate(wizard=True)

feed = sn.timeline
for tweet_item in feed:
    tweet = tweet_item.convert('object')
    print("@{0}: {1}".format(tweet.sender, tweet.text))
