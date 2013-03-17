from datetime import datetime, timedelta

import logging


class CoreManager:
    """Basic abstract social site handeler defining methods that any site must
    implement to be usable in a transparent way"""

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
    UPDATE_SIZE = 10

    def __init__(self, feed_url, **kwargs):
        self.url = feed_url
        self.items = []
        self.logger = logging.getLogger('socyallib.core.feed')

        self.update()

    def __repr__(self):
        return "{0} ({1})".format(self.__class__.__name__, self.url)

    def __iter__(self):
        """A feed is iterable, each iteration return an element"""
        self.iterate_index = 0
        return self

    def next(self):
        if self.iterate_index >= len(self.items):
            # update the content of the items list
            self.read(from_index=self.iterate_index)
            if self.iterate_index >= len(self.items):
                # no more items on the site
                raise StopIteration()
        self.iterate_index += 1
        return self.items[self.iterate_index]

    @property
    def latest(self, **kwargs):
        """Return the latest object of the feed"""
        self.update()
        iterator = iter(self)
        return iterator.next()

    def read(self, count=UPDATE_SIZE, from_index=0, format="dict", **kwargs):
        """Return the content of the feed.

        :param count: the number of items to return in the feed
        :param from_index: the index number of the first item in the feed. The
        content of this index is dependant of the site (unique id or position
        in the online feed).
        :param format: the output format of the feed.
            'raw' a list of items as returned by the website API
            'dict' the internal format common to all webistes
            'rss' representation following the standart RSS2.0
        """
        raise NotImplementedError

    def update(self, force=False):
        """Update the feed"""
        if not self.last_update or force:
            self.logger.info("Updating feed")
            self._update()
            self.last_update = datetime.now()
        else:
            if datetime.now() - self.last_update > self.MAX_UPDATE_DELAY:
                self.logger.info("Updating feed")
                self._update()
                self.last_update = datetime.now()
            else:
                self.logger.info("Updated recently, skipping")

    def _update(self, size=UPDATE_SIZE, **kwargs):
        """Internal update method of a feed

        The self.items list should contains the latest elements, sorted by date
        :param size: The number of elements to retrieve in the feed and add to
        self.items (minus duplicates). In case of a gap between the already
        retrieved items and the new ones, the method tries to remove it by
        another update of size. If there is still a gap atherward, the previous
        items are dropped.
        """
        raise NotImplementedError
