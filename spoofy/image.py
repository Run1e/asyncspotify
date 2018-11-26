
from .object import Object

class Image(Object):
	
	def __str__(self):
		return self.url
	
	def __repr__(self):
		return f'<Image url=\'{self.url}\''
	
	def _fill(self, obj):
		self.url = obj['url']
		self.width = obj['width']
		self.height = obj['height']