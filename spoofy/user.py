
from .object import Object
from .mixins import ExternalURLMixin, ImageMixin

class User(Object, ExternalURLMixin, ImageMixin):
	def __init__(self, data):
		super().__init__(data)
		
		self.display_name = data.pop('display_name')
		self.name = self.display_name
		
		followers = data.get('followers', None)
		self.follower_count = None if followers is None else followers['total']
		
		self._fill_external_urls(data.pop('external_urls'))
		
		images = data.pop('images', None)
		if images is None:
			self.images = []
		else:
			self._fill_images(images)

class PublicUser(User):
	pass

class PrivateUser(User):
	pass