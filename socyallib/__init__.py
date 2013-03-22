"""
    Python library to interact with socyal networking websites
"""

__version__ = "0.0.1"

from .core import CoreManager, CoreFeed
from .oauth1 import OAuth1Manager
from .twitter import Twitter, TwitterFeed
from .statusnet import StatusNet
