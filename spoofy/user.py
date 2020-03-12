from .mixins import ExternalURLMixin, ImageMixin
from .object import Object


class _BaseUser(Object, ExternalURLMixin, ImageMixin):
	_type = 'user'

	def __init__(self, client, data):
		super().__init__(client, data)

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

	async def get_playlists(self):
		'''
		Get the users playlists.
		
		Alias of :meth:`Client.get_user_playlists`
		'''
		return await self._client.get_user_playlists(self.id)


class PublicUser(_BaseUser):
	'''
	Represents a User object.

	id: str
		Spotify ID of the user.
	name: str
		Name of the user. Also aliased to the ``display_name`` attribute.
	images: List[:class:`Image`] or None
		List of associated images, such as the users profile picture.
	uri: str
		Spotify URI of the user.
	link: str
		Spotify URL of the user.
	follower_count: int or None
		Follower count of the user.
	external_urls: dict
		Dictionary that maps type to url.
	'''


class PrivateUser(_BaseUser):
	def __init__(self, client, data):
		super().__init__(client, data)

		self.birthdate = data.pop('birthdate', None)
		self.country = data.pop('country', None)
		self.email = data.pop('email', None)
		self.product = data.pop('product', None)

	async def get_top_tracks(self, limit=20, offset=0):
		'''
		Gets the top tracks of the current user.
		
		Requires scope ``user-top-read``.
		
		:param int limit: How many tracks to return. Maximum is 50.
		:param int offset: The index of the first result to return.
		:return: List[:class:`SimpleTrack`]
		'''

		return await self._client.get_me_top_tracks(limit=limit, offset=offset)

	async def get_top_artists(self, limit=20, offset=0):
		'''
		Get the top artists of the user.
		
		:param int limit: How many artists to return. Maximum is 50.
		:param int offset: The index of the first result to return.
		:return: List[:class:`SimpleArtist`]
		'''

		return await self._client.get_me_top_artists(limit=limit, offset=offset)

	async def create_playlist(self, name='Unnamed playlist', description=None, public=False, collaborative=False):
		'''
		Create a new playlist.
		
		:param str name: Name of the new playlist.
		:param str description: Description of the new playlist.
		:param bool public: Whether the playlist should be public.
		:param bool collaborative: Whether the playlist should be collaborative (anyone can edit it).
		:return: A :class:`FullPlaylist` instance.
		'''

		return await self._client.create_playlist(
			user=self.id,
			name=name,
			description=description,
			public=public,
			collaborative=collaborative
		)
