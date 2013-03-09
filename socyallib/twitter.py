from .oauth1 import OAuth1API


class Twitter(OAuth1API):

    site_type = "twitter"
    api_url = "https://api.twitter.com/"

    client_key = "xuPLvAGVnOFOC9iwXEwg"
    client_secret = "sfZs9VX8hJjCCSvVpuQoOZdRnSCATaejNL2253ITTs8"

    home_timeline_uri = '1.1/statuses/home_timeline.json'
    timeline_url = '1.1/statuses/home_timeline.json'

    def __init__(self, account_name="Twitter"):
        super(Twitter, self).__init__(account_name)
