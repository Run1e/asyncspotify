
from .object import Object
from .artist import SimpleArtist
from .user import User

class SimpleTrack(Object):
	
	def _fill(self, obj):
		for value in ('available_markets', 'disc_number', 'duration_ms', 'explicit',
						'href', 'name', 'preview_url', 'track_number', 'uri', 'is_local'):
			setattr(self, value, obj[value])
			
		self.artists = []
		for artist in obj['artists']:
			self.artists.append(SimpleArtist(id=artist.pop('id'), **artist))
		
class Track(SimpleTrack):
	
	def _fill(self, obj):
		for value in ('explicit', 'popularity'):
			setattr(self, value, obj[value])
		super()._fill(obj)

class PlaylistTrack(Track):
	
	def _fill(self, obj):
		self.added_at = obj['added_at']
		self.added_by = obj['added_by']
		super()._fill(obj['track'])