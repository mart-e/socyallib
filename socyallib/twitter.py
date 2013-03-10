from .oauth1 import OAuth1Manager
from .core import CoreFeed

import requests

import json
import logging
import sys

if sys.version >= '3':
    from urllib.parse import urljoin
else:
    from urlparse import urljoin


class Twitter(OAuth1Manager):

    SITE_TYPE = "twitter"
    API_URL = "https://api.twitter.com/"

    client_key = "xuPLvAGVnOFOC9iwXEwg"
    client_secret = "sfZs9VX8hJjCCSvVpuQoOZdRnSCATaejNL2253ITTs8"

    HOME_TIMELINE_URI = '1.1/statuses/home_timeline.json'
    MENTION_TIMELINE_URI = '1.1/statuses/mentions_timeline.json'
    USER_TIMELINE_URI = '1.1/statuses/user_timeline.json'

    def __init__(self, account_name="Twitter", **kwargs):
        super(Twitter, self).__init__(account_name, **kwargs)
        self.logger = logging.getLogger('socyallib.twitter')

    @property
    def timeline(self, timeline="home"):
        return self.feed(timeline="home")

    def feed(self, timeline="home", user=None, **kwargs):
        """Return a timeline of the Twitter account

        :param timeline: The timeline type that should be returned.
            "home" : Tweets and retweets posted by the user and the users followed
            "user" : Tweets posted by the user
            "mention" : mentions (tweets containing a users's @screen_name)
        :param user: The user concerned by the timeline. This is relevant only
            for the "user" timeline type as the others are not public. The name
            of the user concerned is in the format '@username' or 'username'.
        :return: TwitterFeed object
        """
        if timeline.lower() == "home":
            timeline_url = urljoin(self.API_URL, self.HOME_TIMELINE_URI)
        elif timeline.lower() == "user":
            timeline_url = urljoin(self.API_URL, self.USER_TIMELINE_URI)
        elif timeline.lower() == "mention":
            timeline_url = urljoin(self.API_URL, self.MENTION_TIMELINE_URI)
        else:
            raise ValueError("Unknown timeline {0}".format(timeline))

        if type(user) == str:
            if type[0] == '@':
                user = user[:1]
        self.logger.info("Twitter feed to {0}".format(timeline_url))
        return TwitterFeed(timeline_url, self.oauth, user)


class TwitterFeed(CoreFeed):

    def __init__(self, feed_url, oauth, user):
        self.oauth = oauth
        self.user = user
        super(TwitterFeed, self).__init__(feed_url)
        self.logger = logging.getLogger('Twitter')

    def read(self, count=20, format="dict"):
        data = {'count': count}
        if self.user:
            data['screen_name'] = self.user
        r = requests.get(url=self.url, auth=self.oauth, params=data)
        if r.status_code != 200:
            if 'errors' in r.content:
                for error_msg in r.content['errors']:
                    self.logger.error(error_msg)
            else:
                self.logger.error(r.content)
            return []

        result = []
        items = json.loads(r.content.decode())
        for item in items:
            result.append(self.convert_item(item, format))
        return result

    def convert_item(self, item, format):
        # remove t.co urls
        full_text = item['text']
        for url in item["entities"]["urls"]:
            full_text = full_text.replace(url["url"], url["expanded_url"])

        if format.lower() == "raw":
            return item
        if format.lower() == "dict":
            result = {}
            result['id'] = item['id']
            result['from'] = item['user']['screen_name']
            result['text'] = full_text
            result['date'] = item['created_at']
            return result
        else:
            raise ValueError("Unknown format {0}".format(format))
