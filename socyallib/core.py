from datetime import datetime, timedelta

import logging


class CoreManager(object):
    """Basic abstract social site handeler defining methods that any site must
    implement to be usable in a transparent way"""

    SITE_TYPE = "default"

    def authenticate(self, **kwargs):
        """Authenticate the account.

        Can be verification of credentials, granting authorizations, logging in
        """
        raise NotImplementedError

    @property
    def feed(self, **kwargs):
        """Returns an object inheriting from CoreFeed"""
        raise NotImplementedError

    def post(self, **kwargs):
        """Post action to the site

        :message (str): the message to post
        :attachements (list or str): one filename or a list of filenames (str)
         to attach to the message
        """
        raise NotImplementedError

class CoreFeedItem(object):

    def __init__(self, raw_value):
        self.raw_value = raw_value

    def convert(self, format):
        """Convert a native object into a specified format

        :param format: the outpout format
            raw: the value as returned by the website
            object: use the Struct class to access elements, TODO decide format
            activitystream: json activity stream format
        """
        if format == 'raw':
            return self.raw()
        else:
            raise NotImplementedError

    @property
    def raw(self):
        return self.raw_value

class CoreFeed(object):

    MAX_UPDATE_DELAY = timedelta(minutes=15)
    FEED_SIZE = 20
    ITEM_TYPE = CoreFeedItem

    def __init__(self, feed_url, **kwargs):
        self.url = feed_url
        self.items = []
        self.last_update = None
        self.logger = logging.getLogger(__name__+'core.feed')

        self.update()

    def __str__(self):
        """Return the content of the feed"""
        return "{0} ({1})".format(self.__class__.__name__, self.url)

    @property
    def latest(self, **kwargs):
        """Return the latest object of the feed"""
        self.update()
        iterator = iter(self)
        return iterator.next()

    def fetch(self, count=FEED_SIZE, from_index=0, **kwargs):
        """Fetch the content of the feed online and update the items.

        :param count: the number of items to return in the feed
        :param from_index: the index number of the first item in the feed. The
        content of this index is dependant of the site (unique id or position
        in the online feed).
        :return: a list of CoreFeedItem
        """
        raise NotImplementedError

    def update(self, force=False):
        """Update the feed

        Smart method to update the feed
        """
        if not self.last_update or force:
            self.logger.info("Updating feed")
            self.items = self.fetch()
            self.last_update = datetime.now()
        else:
            if datetime.now() - self.last_update > self.MAX_UPDATE_DELAY:
                self.logger.info("Updating feed")
                self.items = self.fetch()
                self.last_update = datetime.now()
            else:
                self.logger.info("Updated recently, skipping")

    def read(self, format="activitystream", count=FEED_SIZE, from_index=0):
        """Return the content of the feed converted

        :param format: the output format of the feed.
            'raw' a list of items as returned by the website API
            'activitystream' json activity stream format
            'rss' representation following the standart RSS2.0
        """
        out = []
        for item in self.generate(count=count, from_index=from_index):
            out.append(item.convert(format))
        return out

    def generate(self, count, from_index):
        """Generator of the list of elements"""
        iterate_index = 0
        for item in self.items:
            if iterate_index >= count:
                break

            if iterate_index >= len(self.items):
                # update the content of the items list
                iterate_index = self.extend_items(self.fetch(from_index=iterate_index), iterate_index)
                if iterate_index >= len(self.items):
                    # no more items on the site
                    break

            yield self.items[iterate_index]
            iterate_index += 1

    def extend_items(self, new_content, last_index=0):
        """Extend the list of elements with these new elements

        SHOULD do it smartly by checking indexes and avoid duplicates.
        Currently it just append the to lists.
        last_index should be modified if the previous list is modified
        """
        self.items.extend(new_content)
        return iterate_index


class Struct:
    def __init__(self, entries):
        self.__dict__.update(entries)
