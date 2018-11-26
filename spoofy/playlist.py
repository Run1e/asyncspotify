
from .object import Object
from .mixins import UrlMixin, TrackContainerMixin, ImageMixin

class Playlist(Object, UrlMixin, TrackContainerMixin, ImageMixin):
	
	def _fill(self, obj):
		for value in ('id', 'href', 'name', 'description', 'snapshot_id', 'uri', 'collaborative', 'public', 'images', 'snapshot_id'):
			setattr(self, value, obj.get(value, None))
			
		self._fill_urls(obj['external_urls'])
		self._fill_images(obj['images'])

class FullPlaylist(Playlist):
	
	def _fill(self, obj):
		super()._fill(obj)
		
		for value in ('primary_color', 'description'):
			setattr(self, value, obj.get(value, None))
		
		self.follower_count = obj['followers']['total']