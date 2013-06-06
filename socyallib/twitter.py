from .oauth1 import OAuth1Manager
from .core import CoreFeed, CoreFeedItem, Struct

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
    API_URL = "http://api.twitter.com/1.1/"

    client_key = "xuPLvAGVnOFOC9iwXEwg"
    client_secret = "sfZs9VX8hJjCCSvVpuQoOZdRnSCATaejNL2253ITTs8"

    HOME_TIMELINE_URI = 'statuses/home_timeline.json'
    MENTION_TIMELINE_URI = 'statuses/mentions_timeline.json'
    USER_TIMELINE_URI = 'statuses/user_timeline.json'
    POST_URI = 'statuses/update.json'
    POST_ATTACHEMENTS_URI = 'statuses/update_with_media.json'

    def __init__(self, account_name="Twitter", **kwargs):
        super(Twitter, self).__init__(account_name, **kwargs)
        self.logger = logging.getLogger(__name__+'twitter')

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
        self.logger.info("{0} feed to {1}".format(self.SITE_TYPE, timeline_url))
        return TwitterFeed(timeline_url, self.oauth, user)

    def post(self, message="", attachements=None, in_reply_to=None):
        """Post action to the site"""
        if type(message) != str:
            raise ValueError("Unknown message type {0}, should be string".format(type(message)))
        data = {'status': message}

        if attachements:
            uri = self.POST_ATTACHEMENTS_URI
            if type(attachements) == str:
                # one element
                pass
            elif type(attachements) == list:
                if type(attachements[0]) != str:
                    # we know there is at least one element otherwise 'if attachements' would be False
                    raise ValueError("Unknown attachements type {0}, should be a list of filenames (str)".format(type(attachements)))
                else:
                    pass
            else:
                raise ValueError("Unknown attachements type {0}, should be a list of filenames (str)".format(type(attachements)))
            # TODO accept binary content
        else:
            uri = self.POST_URI

        if in_reply_to:
            if type(in_reply_to) == list:
                # can reply to only one element
                in_reply_to = in_reply_to[0]
            if type(in_reply_to) == int:
                data['in_reply_to_status_id'] = in_reply_to
            elif isinstance(in_reply_to, TwitterFeedItem):
                data['in_reply_to_status_id'] = in_reply_to.raw_value['id']
            else:
                raise ValueError("Invalid in_reply_to format %s" % type(in_reply_to))

        url = urljoin(self.API_URL, uri)
        r = requests.post(url=url, auth=self.oauth, params=data)
        if r.status_code != 200:
            self.logger.error(r.content)
            return False
        else:
            self.logger.info("Notice posted")
            return True


class TwitterFeedItem(CoreFeedItem):

    def convert(self, format):
        # remove t.co urls
        full_text = self.raw_value['text']
        if "entities" in self.raw_value and "urls" in self.raw_value["entities"]:
            for url in self.raw_value["entities"]["urls"]:
                full_text = full_text.replace(url["url"], url["expanded_url"])

        if format.lower() == "raw":
            return self.raw_value
        if format.lower() == "activitystream":
            result = {}
            result['id'] = self.raw_value['id']
            result['sender'] = self.raw_value['user']['screen_name']
            result['text'] = full_text
            #result['date'] = datetime.strptime(self.raw_value['created_at'], "%a %b %d %H:%M:%S %z %Y")
            return Struct(result)
        else:
            raise ValueError("Unknown format {0}".format(format))

    @property
    def author(self):
        return self.raw_value["user"]["name"]

    @property
    def author_id(self):
        return self.raw_value["user"]["screen_name"]


class TwitterFeed(CoreFeed):

    ITEM_TYPE = TwitterFeedItem

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
        content = r.content.decode()
        if r.status_code != 200:
            if "errors" in content:
                for error_msg in content["errors"]:
                    self.logger.error(error_msg)
            else:
                self.logger.error(content)
            return []

        result = []
        items = json.loads(content)
        for item in items:
            result.append(self.ITEM_TYPE(item))
        return result

    def _update(self, size, **kwargs):
        data = {'count': size}
        if self.user:
            data['screen_name'] = self.user
        r = requests.get(url=self.url, auth=self.oauth, params=data)
        content = r.content.decode()
        if r.status_code != 200:
            if "errors" in content:
                for error_msg in content["errors"]:
                    self.logger.error(error_msg)
            else:
                self.logger.error(content)
            return []

        items = json.loads(content)
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
