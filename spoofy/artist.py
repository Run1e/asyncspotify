
from .object import Object
from .mixins import ImageMixin

class Artist(Object):
	def _fill(self, obj):
		for value in ('id', 'href', 'name', 'uri'):
			setattr(self, value, obj.get(value, None))

class SimpleArtist(Artist):
	pass

class FullArtist(Artist, ImageMixin):
	def _fill(self, obj):
		super()._fill(obj)
		
		for value in ('followers', 'genres', 'images', 'popularity'):
			setattr(self, value, obj.get(value, None))
			
		self._fill_images(obj['images'])