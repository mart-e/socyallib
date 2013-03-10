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

    @property
    def latest(self, **kwargs):
        """Return the latest object of the feed"""
        raise NotImplementedError

    def read(self, **kwargs):
        """Return the content of the feed. The size of the feed and dates are
        the choice of the subclass implementing it"""
        raise NotImplementedError
