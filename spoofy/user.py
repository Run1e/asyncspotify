
from .object import Object
from .mixins import ExternalURLMixin, ImageMixin

class User(Object, ExternalURLMixin, ImageMixin):
	def __init__(self, client, data):
		super().__init__(client, data)
		
		self.display_name = data.pop('display_name')
		
		followers = data.get('followers', None)
		self.follower_count = None if followers is None else followers['total']
		
		self._fill_external_urls(data.pop('external_urls'))
		
		images = data.pop('images', None)
		if images is None:
			self.images = []
		else:
			self._fill_images(images)
	
	async def get_playlists(self):
		return await self._client.get_user_playlists(self.id)

class PublicUser(User):
	pass

class PrivateUser(User):
	def __init__(self, client, data):
		super().__init__(client, data)
		
		self.birthdate = data.pop('birthdate', None)
		self.country = data.pop('country', None)
		self.email = data.pop('email', None)
		self.product = data.pop('product', None)
		
	async def create_playlist(self, name='Unnamed playlist', description=None, public=False, collaborative=False):
		return await self._client.create_playlist(
			user_id=self.id,
			name=name,
			description=description,
			public=public,
			collaborative=collaborative
		)