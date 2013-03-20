from datetime import datetime, timedelta

import logging


class CoreManager:
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
        """Post action to the site"""
        raise NotImplementedError


class CoreFeed:

    MAX_UPDATE_DELAY = timedelta(minutes=15)
    FEED_SIZE = 20

    def __init__(self, feed_url, **kwargs):
        self.url = feed_url
        self.items = []
        self.last_update = None
        self.logger = logging.getLogger('socyallib.core.feed')

        self.update()

    def __repr__(self):
        return "{0} ({1})".format(self.__class__.__name__, self.url)

    def __str__(self, format="activitystream"):
        """Return the content of the feed"""
        return self.read(format)

    def __iter__(self, count=FEED_SIZE, from_index=0):
        """A feed is iterable, each iteration return an element"""
        self.iterate_index = from_index
        if count:
            self.iterate_max = count
        return self

    def __next__(self):
        if self.iterate_max and self.iterate_index >= self.iterate_max:
            del self.iterate_max
            raise StopIteration

        if self.iterate_index >= len(self.items):
            # update the content of the items list
            self.items.extend(self.fetch(from_index=self.iterate_index))
            if self.iterate_index >= len(self.items):
                # no more items on the site
                raise StopIteration()
        self.iterate_index += 1
        return self.items[self.iterate_index-1]

    def next(self):
        """Compatibility level for python2"""
        return self.__next__()

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

    def read(self, format="activitystream", count=FEED_SIZE):
        """Return the content of the feed converted

        :param format: the output format of the feed.
            'raw' a list of items as returned by the website API
            'activitystream' json activity stream format
            'rss' representation following the standart RSS2.0
        """
        if format.lower() == "activitystream":
            out = []
            for item in self.__iter__(count=count):
                out.append(item.convert(format))
            return out
        elif format.lower() == "rss":
            pass


class CoreFeedItem():

    def __init__(self, raw_value):
        self.raw_value = raw_value

    def convert(self, format):
        """Convert a native object into a specified format

        :param format: the outpout format
            raw: the value as returned by the website
            object: use the Struct class to access elements, TODO decide format
            activitystream: json activity stream format
        """
        raise NotImplementedError

    @property
    def raw(self):
        return self.raw_value


class Struct:
    def __init__(self, entries):
        self.__dict__.update(entries)
