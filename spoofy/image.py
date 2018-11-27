
from .object import Object

class Image(Object):
	
	def __init__(self, data):
		super().__init__(data)
		self.url = data.pop('url')
		self.width = data.pop('width')
		self.height = data.pop('height')
	
	def __str__(self):
		return self.url
	
	def __repr__(self):
		return f'<Image url=\'{self.url}\''