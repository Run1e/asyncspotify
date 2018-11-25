
from .object import Object

class SimpleArtist(Object):
	def _fill(self, obj):
		for value in ('href', 'name', 'uri'):
			setattr(self, value, obj[value])
			
class Artist:
	def _fill(self, obj):
		pass