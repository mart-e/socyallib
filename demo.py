#!/usr/bin/env python

from socyallib import Twitter

tw = Twitter(configuration_file="socyallib/config.json")
feed = tw.timeline
for tweet_item in feed:
    tweet = tweet_item.convert('object')
    print("@{0}: {1}".format(tweet.sender, tweet.text))
