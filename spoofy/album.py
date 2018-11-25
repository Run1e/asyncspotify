
from .object import Object
from .artist import SimpleArtist

class Album(Object):
	
	def _fill(self, obj):
		for value in ('album_group', 'album_type', 'available_markets', 'href', 'name', 'uri'):
			setattr(self, value, obj.get(value, None))
			
		self.artists = []
		for artist in obj['artists']:
			self.artists.append(SimpleArtist(**artist))
			
		"""
		external_urls
		release_date
		release_date_precision
		restrictions
		"""

class SimpleAlbum(Album):
	pass

class FullAlbum(Album):
	
	def _fill(self, obj):
		super()._fill(obj)
		
		for value in ('genres', 'label', 'popularity'):
			setattr(self, value, obj[value])
			
			
		"""
		copyrights
		external_ids
		
		"""
		
	async def _fill_tracks(self, pager):
		from .track import SimpleTrack
		
		self.tracks = []
		async for track in pager:
			trck = SimpleTrack(**track)
			trck.playlist = self
			self.tracks.append(trck)