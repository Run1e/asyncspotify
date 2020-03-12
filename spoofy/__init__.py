"""
A Python library for interacting asynchronously with the Spotify API
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
from .playlist import SimplePlaylist, FullPlaylist
from .track import SimpleTrack, FullTrack, PlaylistTrack
from .album import SimpleAlbum, FullAlbum
from .image import Image
from .artist import SimpleArtist, FullArtist
from .user import PrivateUser, PublicUser

from .device import Device
from .playing import CurrentlyPlaying, CurrentlyPlayingContext

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
# log.addHandler(StreamHandler())
