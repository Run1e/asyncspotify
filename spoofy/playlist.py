
from .object import Object
from .track import Track as TrackModel
from .mixins import UrlMixin, TrackMixin, ImageMixin

class Playlist(Object, UrlMixin, TrackMixin, ImageMixin):
	
	def _fill(self, obj):
		for value in ('id', 'href', 'name', 'description', 'snapshot_id', 'uri', 'collaborative', 'public', 'images', 'snapshot_id'):
			setattr(self, value, obj.get(value, None))
			
		self._fill_urls(obj['external_urls'])
		self._fill_images(obj['images'])
		
	def _fill_events(self, client):
		self._add_tracks = client._playlist_add_tracks
		
	async def add_track(self, track, position=0):
		await self._add_tracks(self.id, [track], position=position)
		if isinstance(track, TrackModel):
			self._tracks[track.id] = track
			
	async def add_tracks(self, *tracks, position=0):
		await self._add_tracks(self.id, tracks, position=position)
		for track in filter(lambda track: isinstance(track, TrackModel), tracks):
			self._tracks[track.id] = track

class FullPlaylist(Playlist):
	
	def _fill(self, obj):
		super()._fill(obj)
		
		for value in ('primary_color', 'description'):
			setattr(self, value, obj.get(value, None))
		
		self.follower_count = obj['followers']['total']