#!/usr/bin/env python

from socyallib import Twitter, StatusNet
import logging
logger = logging.getLogger('socyallib')
logger.setLevel(logging.DEBUG)

print("Twitter")
tw = Twitter(configuration_file="config.json")
tw.authenticate(wizard=True)

for tweet in tw.timeline.read(format='activitystream'):
    print("@%s: %s" % (tweet.sender, tweet.text))


print("StatusNet")
sn = StatusNet(configuration_file="config.json")
sn.authenticate(wizard=True)

for tweet in sn.timeline.read(format='activitystream'):
    print("@%s: %s" % (tweet.sender, tweet.text))