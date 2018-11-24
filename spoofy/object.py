
class Object:
	def __str__(self):
		return f'<{self.__class__.__name__} id=\'{self.id}\' name=\'{self.name}\'>'