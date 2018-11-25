
from .pager import Pager

from .object import Object
from .track import PlaylistTrack

class Playlist(Object):
	pass

class FullPlaylist(Object):
	
	def _fill(self, obj):
		for value in ('href', 'name', 'description', 'snapshot_id', 'uri', 'collaborative', 'public', 'images'
					  , 'primary_color', 'snapshot_id'):
			setattr(self, value, obj[value])
			
		self.url = obj['external_urls']['spotify']
		self.followers = obj['followers']['total']
		
		self.tracks = []
		
	async def _fill_tracks(self, pager):
		async for track in pager:
			self.tracks.append(PlaylistTrack(id=track['track'].pop('id'), **track))