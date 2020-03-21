"""
A Python library for interacting asynchronously with the Spotify API
"""

__title__ = 'asyncspotify'
__author__ = 'RUNIE'
__version__ = '0.11.1'
__license__ = 'MIT'

import logging

from . import utils
from .album import FullAlbum, SimpleAlbum
from .artist import FullArtist, SimpleArtist
from .client import Client
from .device import Device
from .exceptions import *
from .image import Image
from .oauth import AuthorizationCodeFlow, ClientCredentialsFlow, EasyCodeFlow
from .object import Object
from .playing import CurrentlyPlaying, CurrentlyPlayingContext
from .playlist import FullPlaylist, SimplePlaylist
from .scope import Scope
from .track import FullTrack, PlaylistTrack, SimpleTrack
from .user import PrivateUser, PublicUser

log = logging.getLogger(__name__)
log.setLevel(logging.WARNING)
