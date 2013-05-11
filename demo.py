#!/usr/bin/env python

from socyallib import Twitter, StatusNet
import logging
logging.basicConfig(filename="socyallib.log", level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %H:%M:%S')
logger = logging.getLogger('socyallib')

print("Twitter")
tw = Twitter(configuration_file="config.json")
tw.authenticate(wizard=True)

for tweet in tw.timeline.read(format='activitystream'):
    print("@%s: %s" % (tweet.sender, tweet.text))


print("\nStatusNet")
sn = StatusNet(configuration_file="config.json")
sn.authenticate(wizard=True)

for tweet in sn.timeline.read(format='activitystream'):
    print("@%s: %s" % (tweet.sender, tweet.text))