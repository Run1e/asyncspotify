
from datetime import timedelta

from .object import Object
from .artist import SimpleArtist
from .album import SimpleAlbum


class Track(Object):
	def __str__(self):
		return f'{self.artists[0].name} - {self.name}'
	
	def _fill(self, obj):
		for value in ('available_markets', 'disc_number', 'explicit', 'href', 'name', 'preview_url', 'track_number',
					  'uri', 'is_local'):
			setattr(self, value, obj[value])
		
		self.length = timedelta(milliseconds=obj['duration_ms'])
		
		self.artists = []
		for artist in obj['artists']:
			self.artists.append(SimpleArtist(id=artist.pop('id'), **artist))
	
	def avaliable_in(self, region):
		return region in self.available_markets

class SimpleTrack(Track):
	pass
		
class FullTrack(Track):
	
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
	
	def _fill(self, obj):
		super()._fill(obj)
		
		for value in ('explicit', 'popularity'):
			setattr(self, value, obj[value])
			
		self.album = SimpleAlbum(**obj['album'])

class PlaylistTrack(FullTrack):
	
	def _fill(self, obj):
		self.added_at = obj['added_at']
		self.added_by = obj['added_by']
		super()._fill(obj['track'])