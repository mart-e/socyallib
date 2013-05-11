from .oauth1 import OAuth1Manager
from .twitter import Twitter
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


class StatusNet(Twitter):

    SITE_TYPE = "statusnet"
    API_URL = "https://identi.ca/api/"  # to change for other instances

    client_key = "913c61308b2907177fbd38a07fb794b5"
    client_secret = "bd40d48b83e35025c5881571e33bcc80"

    HOME_TIMELINE_URI = 'statuses/home_timeline.json'
    MENTION_TIMELINE_URI = 'statuses/mentions_timeline.json'
    USER_TIMELINE_URI = 'statuses/user_timeline.json'

    def __init__(self, account_name="StatusNet", **kwargs):
        super(StatusNet, self).__init__(account_name, **kwargs)
        self.logger = logging.getLogger(__name__+'statusnet')
