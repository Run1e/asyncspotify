"""
from .album import FullAlbum, SimpleAlbum
from .artist import FullArtist, SimpleArtist
from .playlist import FullPlaylist, SimplePlaylist
from .track import FullTrack, SimpleTrack
from .user import PublicUser, PrivateUser
"""

_cache = {}

def cache(init):
	def cache_check(self, *args, **kwargs):
		pass