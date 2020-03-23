class SpotifyObject:
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

	def __eq__(self, other):
		return self.id == other.id

	def __ne__(self, other):
		return not self.__eq__(other)

	def __repr__(self):
		repr = self.__class__.__name__
		if self.id is not None:
			repr += ' id=\'{}\''.format(self.id)
		if self.name is not None:
			repr += ' name=\'{}\''.format(self.name)
		return '<%s>' % repr
