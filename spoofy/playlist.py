
from .object import Object

class Playlist(Object):
	
	_map = ('id', 'href', 'name', 'snapshot_id', 'uri', 'collaborative', 'public')
	
	def __init__(self, obj):
		self._fill(obj)
		
	def _fill(self, obj):
		for value in self._map:
			setattr(self, value, obj[value])