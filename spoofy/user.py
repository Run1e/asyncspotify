
from .object import Object

class User(Object):
	pass

class PrivateUser(User):
	
	def _fill(self, obj):
		for value in ('birthdate', 'country', ):
			setattr(self, value, obj.get(value, None))

class PublicUser(User):
	
	def _fill(self, obj):
		for value in ('display_name', 'href', 'uri'):
			setattr(self, value, obj.get(value, None))
			
		self.name = self.display_name
		print(self.name)
