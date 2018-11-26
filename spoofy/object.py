


class Object:
	def __init__(self, **kwargs):
		if hasattr(self, '_fill'):
			self._fill(kwargs)
	
	def __repr__(self):
		return f'<{self.__class__.__name__} id=\'{self.id}\' name=\'{self.name}\'>'
	
	def __str__(self):
		if hasattr(self, 'name'):
			return self.name
		else:
			return self.__repr__()