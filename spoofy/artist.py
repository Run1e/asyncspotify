
from .object import Object

class Artist(Object):
	def _fill(self, obj):
		for value in ('href', 'name', 'uri'):
			setattr(self, value, obj[value])

class SimpleArtist(Artist):
	pass

class FullArtist(Artist):
	def _fill(self, obj):
		super()._fill(obj)
		
		for value in ('followers', 'genres', 'images', 'popularity'):
			setattr(self, value, obj[value])