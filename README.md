Python Sociallib
================

_This lib is still a work in progress. There is nothing usable yet._

Social networking websites are made for humans and let them interact between each other using (more or less) nice UI. Developpers are human too (more or less) and should be able to create easily apps interacting with these websites through API. You have to use OAuth, make HTTPS requests, manage tokens,... Let's make that easy. This is was this lib is about.

    >>> ic = Twitter()
    >>> tw.connect(wizard=True)
    Go to https://api.twitter.com/oauth/authorize?oauth_token=FFNXDEA... and authorize the application.
    Verifier: 123456
    Account authenticated
    >>> tw.post("Long live API !")
    >>> timeline = tw.getFeed()
    >>> timeline.read()
    [{'from':'@duckduckgo','text':'Happy birthday to @Raspberry_Pi !! Big things come in small packages : )',...

Websites often provide activity feeds in their own format which makes the hell of a job for developpers to mix feeds from different websites in one application. That should not be the case.

    >>> feed = tw.getFeed(user="@ThePSF")
    >>> feed.read(format="RSS")
    <?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0"...

Dealing with attachements should not be harder than dealing with text.

    >>> tw.post("Look at this cute picture", attachement="cat.png")
    >>> feed.latest.attachement.save("myfile.jpg")

We do not like URL trimming. You can use it to save a few characters but we want the full URL for apps.

    >>> feed.latest.raw
    {..., "text":"I just bought sushi. Look ! http://t.co/9G8WTYstd3",...
    >>> feed.latest.text
    I just bought sushi. Look ! http://instagram.com/p/Wpxz6cnU2k/

Different websites works differently but we want to have the same syntaxe to interact with them. We use neutral terms such as "account", "feed", "post", "repeat" that are adapted depending on the website. The action `like()` on Facebook will have the same effect as the btuton "I like" but on Twitter, it will favorite de Tweet and on Google+, it will act as the "+1" button.

# Websites planned to be supported

Several websites are planned to be supported through the app. More or less in planned the order :

* OAuth1 (through requests-oauthlib)
  * Twitter
  * Status.Net
    * identi.ca
  * Pump
* OAuth2 (through requests-oauth2)
  * Facebook
  * Google+
  * Tent
