"""
from .album import FullAlbum, SimpleAlbum
from .artist import FullArtist, SimpleArtist
from .playlist import FullPlaylist, SimplePlaylist
from .track import FullTrack, SimpleTrack
from .user import PublicUser, PrivateUser
"""

class Cacher:
	
	_cache = {}
	
	@classmethod
	def return_exists(cls, id):
		if id in cls._cache:
			#print('YAAAAAAAAAAAAAAAAAAAAAAAAS')
			return cls._cache[id]
		else:
			#print('nah')
			return None
	
	@classmethod
	def on_object_create(cls, object):
		cls._cache[object.id] = object