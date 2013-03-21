# API keys

The OAuth keys required to interact with the servers are hardcoded in some python files. By the open source nature of this library, it is hard and mostly inefficient to try to hide these keys. These keys are provided as an example and for testing purpose and should NOT be used for production. I highly recommand you to change these keys by the one for an application you register.

Using API keys published on the internet means than any application can use it and increase the chance of misused and revocation. In addition, websites such as Twitter put a strict limitation on the number of calls and application can make.

In case of key revocation by the website or limit exceeded, I do NOT ensure the key will be replaced. I may replace it at the next release but using your own keys is the best solution.

## Using your own OAuth key/secret

To use your own keys, you can either put in the configuration file (first argument of the `load` method) with the `client_key` and `client_secret` key or set the class attributes with the same name.

    "MyStatusNet":{
            "site_type":"statusnet",
            "client_key": "7812bf791fb6486fx09b48c6e514aadb", 
            "client_secret": "sfZw9VX8HJjCCdvVp8QoO5drnScATaejNL2253ITTs0"
    }

## Twitter

To register a new application go to https://dev.twitter.com/apps/new (you will need to create a developper account).

## StatusNet

To register a new application go to your StatusNet instance at the URI /settings/oauthapps. For instancence, with identi.ca, the full URL is https://identi.ca/settings/oauthapps