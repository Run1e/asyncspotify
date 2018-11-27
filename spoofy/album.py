
from .object import Object
from .mixins import UrlMixin, TrackMixin, ImageMixin, ArtistMixin

class Album(Object, UrlMixin, TrackMixin, ImageMixin, ArtistMixin):
	
	def _fill(self, obj):
		for value in ('id', 'album_group', 'album_type', 'available_markets', 'href', 'name', 'uri'):
			setattr(self, value, obj.get(value, None))
			
		self._fill_urls(obj['external_urls'])
		self._fill_artists(obj['artists'])
		self._fill_images(obj['images'])
		
		"""
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
			setattr(self, value, obj.get(value, None))
			
			
		"""
		copyrights
		external_ids
		
		"""