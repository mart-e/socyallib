# Social Account

Constants :
    SITE_TYPE : the name of the social network configured

Class attributes :
    account_name : the name of the configured, should be unique

Methods :
    authenticate : create a connection to the website and grant access to ressources if not configured
    feed : return a feed object
    post : send an update to the network

# Feed

Methods :
    __iter__ : return FeedItem objects
    read : return a representation of the feed in a chosen format
    fetch : get items online
    update : reload the list of items (+ cache)