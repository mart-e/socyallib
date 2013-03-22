Python Sociallib
================

_This lib is still a work in progress. There is nothing usable yet._

Version 0.0.1 (I told you there is nothing usable yet)

Social networking websites are made for humans and let them interact between each other using (more or less) nice UI. Developpers are human too (more or less) and should be able to create easily apps interacting with these websites through API. You have know how to use OAuth, make HTTPS requests, manage tokens,... Let's make that easy. This is was this lib is about.

    >>> tw = Twitter()
    >>> tw.authenticate(wizard=True)
    Go to https://api.twitter.com/oauth/authorize?oauth_token=FFNXDEA... and authorize the application.
    Verifier: 123456
    Account authenticated
    >>> tw.post("Long live API !")
    >>> for tweet in tw.timeline(count=20):
    ...   print(tweet.text)

Websites often provide activity feeds in their own format which makes the hell of a job for developpers to mix feeds from different websites in one application. That should not be the case.

    >>> feed = tw.feed(user="@ThePSF")
    >>> feed.read(format="RSS")
    <?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0"...

Dealing with attachements should not be harder than dealing with text.

    >>> tw.post("Look at this cute picture", attachements=["cat.png"])
    >>> feed.latest.attachements[0].save("myfile.jpg")

We do not like URL trimming. You can use it to save a few characters but we want the full URL for apps.

    >>> feed.latest.raw
    {..., "text":"I just bought sushi. Look ! http://t.co/9G8WTYstd3",...
    >>> feed.latest.text
    I just bought sushi. Look ! http://instagram.com/p/Wpxz6cnU2k/

Different websites work differently but we want to have the same syntaxe to interact with them. The verbs used are neutral and based on [Activity Stream Verbs](http://activitystrea.ms/specs/json/schema/activity-schema.html) that are adapted depending on the website. The action `like()` on Facebook will have the same effect as the button "I like" but on Twitter, it will favorite de Tweet and on Google+, it will act as the "+1" button.

## Websites planned to be supported

Several protocols and websites are planned to be supported through the app. More or less in planned the order :

* OAuth1 (through requests-oauthlib)
  * Twitter
  * Status.Net
    * identi.ca
  * Pump
* OAuth2 (through requests-oauth2)
  * Facebook
  * Google+
  * Tent
* RSS ?
