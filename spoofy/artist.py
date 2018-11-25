
from .object import Object

class Artist(Object):
	pass

class SimpleArtist(Artist):
	def _fill(self, obj):
		for value in ('href', 'name', 'uri'):
			setattr(self, value, obj[value])