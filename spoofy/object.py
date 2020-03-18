class Object:
	'''
	Represents a generic Spotify Object.
	
	Attributes
	----------
	
	id: str
		Spotify ID of the object.
	name: str
		Name of the object.
	uri: str
		Spotify URI of the object.
		
	'''

	_type = None

	def __init__(self, client, data):
		self._client = client
		self.id = data.pop('id', None)
		self.name = data.pop('name', None)
		self.href = data.pop('href', None)
		self.uri = data.pop('uri', None)

	@property
	def type(self):
		return self._type

	def __repr__(self):
		repr_str = self.__class__.__name__
		if self.id:
			repr_str += ' id=\'{}\''.format(self.id)
		if self.name:
			repr_str += ' name=\'{}\''.format(self.name)
		return '<{}>'.format(repr_str)
