
from .object import Object
from .track import PlaylistTrack

class Playlist(Object):
	pass

class FullPlaylist(Playlist):
	
	def _fill(self, obj):
		for value in ('href', 'name', 'description', 'snapshot_id', 'uri', 'collaborative', 'public', 'images'
					  , 'primary_color', 'snapshot_id'):
			setattr(self, value, obj[value])
		
		self.url = obj['external_urls']['spotify']
		self.followers = obj['followers']['total']
	
	async def _fill_tracks(self, pager):
		self.tracks = []
		async for track in pager:
			trck = PlaylistTrack(id=track['track'].pop('id'), **track)
			trck.playlist = self
			self.tracks.append(trck)