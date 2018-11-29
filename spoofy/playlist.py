
from .object import Object
from .track import Track as TrackModel
from .user import PublicUser
from .mixins import ExternalURLMixin, TrackMixin, ImageMixin, UserMixin

from pprint import pprint


class Playlist(Object, ExternalURLMixin, TrackMixin, ImageMixin, UserMixin):
	
	_type = 'playlist'
	
	def __init__(self, client, data):
		super().__init__(client, data)
		
		self._tracks = {}
		
		self.snapshot_id = data.pop('snapshot_id')
		self.collaborative = data.pop('collaborative')
		self.public = data.pop('public')
		
		self.owner = PublicUser(client, data.pop('owner'))
		
		self._fill_external_urls(data.pop('external_urls'))
		self._fill_images(data.pop('images'))
	
	async def edit(self, name=None, description=None, public=None, collaborative=None):
		await self._client.http.edit_playlist(self.id, name=name, description=description, public=public, collaborative=collaborative)
	
	async def add_track(self, track, position=0):
		await self._client.playlist_add_tracks(self.id, [track], position=position)
		if isinstance(track, TrackModel):
			self._tracks[track.id] = track
			
	async def add_tracks(self, *tracks, position=0):
		await self._client.playlist_add_tracks(self.id, tracks, position=position)
		for track in filter(lambda track: isinstance(track, TrackModel), tracks):
			self._tracks[track.id] = track

class SimplePlaylist(Playlist):
	pass

class FullPlaylist(Playlist):
	
	def __init__(self, client, data):
		super().__init__(client, data)
		
		self.description = data.pop('description')
		self.primary_color = data.pop('primary_color')
		self.follower_count = data['followers']['total']
		