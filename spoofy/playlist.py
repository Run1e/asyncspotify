
from .object import Object

class Playlist(Object):
	
	_map = ('href', 'name', 'snapshot_id', 'uri', 'collaborative', 'public')
		
	def _fill(self, obj):
		for value in self._map:
			setattr(self, value, obj[value])