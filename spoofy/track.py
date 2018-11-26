
from datetime import datetime, timedelta

from .object import Object
from .artist import SimpleArtist
from .album import SimpleAlbum
from .user import PublicUser
from .mixins import UrlMixin, ArtistMixin


class Track(Object, UrlMixin, ArtistMixin):
	def _fill(self, obj):
		for value in ('id', 'available_markets', 'disc_number', 'explicit', 'href', 'name', 'preview_url', 'track_number', 'uri', 'is_local'):
			setattr(self, value, obj.get(value, None))
		
		self.length = timedelta(milliseconds=obj['duration_ms'])
		
		self._fill_urls(obj['external_urls'])
		self._fill_artists(obj['artists'])
	
	def avaliable_in(self, region):
		return region in self.available_markets

class SimpleTrack(Track):
	pass
		
class FullTrack(Track):
	
	def _fill(self, obj):
		super()._fill(obj)
		
		for value in ('explicit', 'popularity'):
			setattr(self, value, obj.get(value, None))
			
		self.album = SimpleAlbum(**obj['album'])

class PlaylistTrack(FullTrack):
	
	def _fill(self, obj):
		super()._fill(obj['track'])
		self.added_at = datetime.strptime(obj['added_at'], "%Y-%m-%dT%H:%M:%SZ")
		self.added_by = obj['added_by']
