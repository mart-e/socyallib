from .oauth1 import OAuth1Manager
from .core import CoreFeed, CoreFeedItem

from datetime import datetime
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
    def timeline(self):
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
        self.logger = logging.getLogger('socyallib.core.feed')

    def fetch(self, count=CoreFeed.FEED_SIZE, from_index=0, **kwargs):
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
            result.append(TwitterFeedItem(item))
        return result

    def _update(self, size, **kwargs):
        data = {'count': size}
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

        items = json.loads(r.content.decode())
        sorted_items = sorted(items, key=lambda k: k['date'], invert=True)
        last_date = datetime.strftime("%a %b %d %H:%M:%S %z %Y", sorted_items[-1]['created_at'])
        if len(self.items) > 0:
            first_stored_date = datetime.strftime("%a %b %d %H:%M:%S %z %Y", self.items[0]['created_at'])
            if last_date < first_stored_date:
                # merge two lists
                pass
            else:
                # retieve next batch of items
                pass


class TwitterFeedItem(CoreFeedItem):

    def convert(self, format):
        # remove t.co urls
        full_text = self.raw_value['text']
        for url in self.raw_value["entities"]["urls"]:
            full_text = full_text.replace(url["url"], url["expanded_url"])

        if format.lower() == "raw":
            return self.raw_value
        if format.lower() == "dict":
            result = {}
            result['id'] = self.raw_value['id']
            result['from'] = self.raw_value['user']['screen_name']
            result['text'] = full_text
            result['date'] = datetime.strptime(self.raw_value['created_at'], "%a %b %d %H:%M:%S %z %Y")
            return result
        else:
            raise ValueError("Unknown format {0}".format(format))
