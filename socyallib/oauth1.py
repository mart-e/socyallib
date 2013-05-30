from .core import CoreManager
from requests_oauthlib import OAuth1
import requests

import json
import logging
import os
import sys

if sys.version >= '3':
    from urllib.parse import parse_qs, urljoin
else:
    from urlparse import parse_qs, urljoin
    input = raw_input


class OAuth1Manager(CoreManager):

    SITE_TYPE = "default"
    API_URL = "https://api.example.com/"

    REQUEST_TOKEN_URI = 'oauth/request_token'
    REQUEST_ARGS = ''
    AUTHORIZE_URI = 'oauth/authorize?oauth_token='
    ACCESS_TOKEN_URI = 'oauth/access_token'

    client_key = None
    client_secret = None
    token = None
    token_secret = None

    def __init__(self, account_name="Default", configuration_file=None):
        """Create an OAuth1 accound handler object

        :param account_name: The name of the account to differentiate two
        configuration of the same network but with different parameters
        :param configuration_file: Path to the JSON configuration file
        containing the keys and parameters of the account. Absolute path name
        is adviced. If no file is specified, will use the keys and tokens
        hardcoded in the library and will not save it if changed during the
        execution (eg: the retrieved token keys and secrets won't be stored).
        It is the responsability of the program to handle the storage of
        credentials."""
        self.account_name = account_name
        self.logger = logging.getLogger(__name__+'oauth1')

        if configuration_file is None:
            self.store_configuration = False
        else:
            self.store_configuration = True
            self.load(configuration_file)

        if self.client_key and self.client_secret:
            self.authenticate()

    def load(self, configuration_file="config.json"):
        """Load the configuration

        :param configuration_file: path to JSON config file containing the
        account information following the structure in config.json.example. The
        configuration of an account should at least contain 'site_type',
        'client_key' and 'client_secret'.
        """
        self.configuration_file = configuration_file

        filename = os.path.abspath(self.configuration_file)
        if not os.path.isfile(filename):
            raise IOError("Config file not found {0}".format(filename))

        with open(filename, 'r') as f:
            config = json.load(f)

        assert self.account_name in config, "Invalid config file, no account found for {0}".format(self.account_name)
        account_config = config[self.account_name]

        if 'api_url' in account_config:
            self.API_URL = account_config['api_url']
        if 'request_token_uri' in account_config:
            self.REQUEST_TOKEN_URI = account_config['request_token_uri']
        if 'authorize_uri' in account_config:
            self.AUTHORIZE_URI = account_config['authorize_uri']
        if 'access_token_uri' in account_config:
            self.ACCESS_TOKEN_URI = account_config['access_token_uri']

        # client key and client secret are mandatory
        assert 'client_key' in account_config, "Invalid config file, no client key found for account {0}".format(self.account_name)
        self.client_key = str(account_config['client_key'])
        assert 'client_secret' in account_config, "Invalid config file, no client secret found for account {0}".format(self.account_name)
        self.client_secret = str(account_config['client_secret'])

        if 'token' in account_config:
            self.token = str(account_config['token'])
        if 'token_secret' in account_config:
            self.token_secret = str(account_config['token_secret'])

    def authenticate(self, wizard=False, verify=True):
        """Connect the account

        Connect to the service and retrieves tokens if none are available.
        :param wizard: Enables assisted authentication process in the terminal
        if no tokens are available. Applications with GUI will most likely not
        enable this parameter and use self.get_authorization_url() followed by
        self.retrieve_tokens() to retrieve the same informations
        :param verify: Verify the validity of the tokens if true
        :type wizard: boolean
        :type verify: boolean
        :return: True if the authentication was successful
        """
        if self.token and self.token_secret:
            if not verify or self.verify_tokens():
                self.oauth = OAuth1(self.client_key,
                                    client_secret=self.client_secret,
                                    resource_owner_key=self.token,
                                    resource_owner_secret=self.token_secret)
                return True
            else:
                self.logger.error("Invalid tokens")
                return False
        else:
            if wizard:
                authorize_url = self.get_authorization_url()
                if authorize_url:
                    print('Go to {0} and authorize the application'.format(authorize_url))
                    verifier = input('Please input the verifier: ')
                    (self.token, self.token_secret) = self.retrieve_tokens(verifier)
                    self.oauth = OAuth1(self.client_key,
                                        client_secret=self.client_secret,
                                        resource_owner_key=self.token,
                                        resource_owner_secret=self.token_secret)
                    return True
                else:
                    self.logger.warning("Invalid authorize url")
                    return False
            else:
                self.logger.warning("No tokens in manual mode, not authenticated")
                return False

    def verify_tokens(self):
        """Verify the validy of tokens

        This procedure should be overwriten by subclasses by making a request
        to verify the validity of the tokens. The verification request should
        not impact the online account (no modification), eg: read user stats.
        """
        return self.token and self.token_secret

    def get_authorization_url(self):
        """Get the URL to authorize the application

        The authorization page will give a verifier code that should be used
        to get the final tokens."""
        oauth = OAuth1(self.client_key, client_secret=self.client_secret)
        request_token_url = urljoin(self.API_URL, self.REQUEST_TOKEN_URI)
        r = requests.post(url=request_token_url+self.REQUEST_ARGS, auth=oauth)
        if r.status_code != 200:
            self.logger.error(r.content)
            return False
        credentials = parse_qs(r.content.decode())
        self.temporary_token = credentials.get('oauth_token')[0]
        self.temporary_token_secret = credentials.get('oauth_token_secret')[0]

        return urljoin(self.API_URL, self.AUTHORIZE_URI+self.temporary_token)

    def retrieve_tokens(self, verifier):
        """Retrieve the oauth tokens and store them in the config file

        :param verifier: the verifier code given on the authorization page
        :return: (oauth_token, oauth_token_secret)
        """
        oauth = OAuth1(self.client_key,
                       client_secret=self.client_secret,
                       resource_owner_key=self.temporary_token,
                       resource_owner_secret=self.temporary_token_secret,
                       verifier=str(verifier))
        access_token_url = urljoin(self.API_URL, self.ACCESS_TOKEN_URI)
        r = requests.post(url=access_token_url, auth=oauth)
        credentials = parse_qs(r.content.decode())
        if 'oauth_token' not in credentials or 'oauth_token_secret' not in credentials:
            raise ValueError("Could not retrieve the OAuth Tokens")

        self.token = credentials.get('oauth_token')[0]
        self.token_secret = credentials.get('oauth_token_secret')[0]
        if self.store_configuration:
            self.write_config()

        return (self.token, self.token_secret)

    def write_config(self):
        """Write the account configuration parameters to self.configuration_file"""
        filename = os.path.abspath(self.configuration_file)
        if os.path.isfile(filename):
            with open(filename, 'r') as f:
                config = json.load(f)
        else:
            # create new config file
            config = {}

        if self.account_name not in config:
            config[self.account_name] = {}

        config[self.account_name]['site_type'] = str(self.SITE_TYPE)
        config[self.account_name]['client_key'] = str(self.client_key)
        config[self.account_name]['client_secret'] = str(self.client_secret)
        config[self.account_name]['token'] = str(self.token)
        config[self.account_name]['token_secret'] = str(self.token_secret)

        with open(filename, 'w') as f:
            json.dump(config, f, sort_keys=True, indent=4, separators=(',', ': '))
