


class Object:
	def __init__(self, id, **kwargs):
		self.id = id
		if hasattr(self, '_fill'):
			self._fill(kwargs)
		
	def __str__(self):
		return f'<{self.__class__.__name__} id=\'{self.id}\' name=\'{self.name}\'>'