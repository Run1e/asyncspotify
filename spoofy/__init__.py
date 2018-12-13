"""
A Python library for interacting asyncronously with the Spotify API
"""

__title__ = 'spoofy'
__author__ = 'RUNIE'
__version__ = '0.10.2'

import logging
from logging import StreamHandler

from .client import Client
from .oauth import OAuth, easy_auth
from . import utils
from .exceptions import *

from .object import Object
from .playlist import Playlist, SimplePlaylist, FullPlaylist
from .track import Track, SimpleTrack, FullTrack, PlaylistTrack
from .album import Album, SimpleAlbum, FullAlbum
from .image import Image
from .artist import Artist, SimpleArtist, FullArtist
from .user import User, PrivateUser, PublicUser

from .device import Device
from .playing import CurrentlyPlaying, CurrentlyPlayingContext

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
# log.addHandler(StreamHandler())
