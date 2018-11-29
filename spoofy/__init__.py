
"""
A Python library for interacting asyncronously with the Spotify API
"""

__title__ = 'spoofy'
__author__ = 'RUNIE'
__version__ = '0.1a'

import logging
from logging import StreamHandler

from .client import Client
from .oauth import OAuth, easy_auth
from .scope import Scope
from . import utils
from .exceptions import *

from .object import Object
from .playlist import Playlist, SimplePlaylist, FullPlaylist
from .track import Track, SimpleTrack, FullTrack, PlaylistTrack
from .album import Album, SimpleAlbum, FullAlbum
from .image import Image
from .artist import Artist, SimpleArtist, FullArtist
from .user import User, PrivateUser, PublicUser

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
log.addHandler(StreamHandler())