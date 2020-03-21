class Image:
	def __init__(self, data):
		self.url = data.pop('url')
		self.width = data.pop('width')
		self.height = data.pop('height')

	def __str__(self):
		return self.url

	def __repr__(self):
		return '<Image url=\'{}\''.format(self.url)
