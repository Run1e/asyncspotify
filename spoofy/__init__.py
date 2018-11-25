
"""
A Python library for interacting asyncronously with the Spotify API
"""

__title__ = 'spoofy'
__author__ = 'RUNIE'
__version__ = '0.1a'

from .client import Client
from .oauth import OAuth
from .exceptions import *

from .playlist import Playlist
from .track import Track