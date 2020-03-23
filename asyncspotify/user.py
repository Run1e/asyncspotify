from .mixins import ExternalURLMixin, ImageMixin
from .object import SpotifyObject


class _BaseUser(SpotifyObject, ExternalURLMixin, ImageMixin):
	_type = 'user'

	def __init__(self, client, data):
		super().__init__(client, data)

		ExternalURLMixin.__init__(self, data)
		ImageMixin.__init__(self, data)

		self.display_name = data.pop('display_name')
		self.name = self.display_name

		followers = data.get('followers', None)
		self.follower_count = None if followers is None else followers['total']

	async def playlists(self):
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
	images: List[:class:`Image`]
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
	'''
	Represents a private User object, usually fetched through the ``me`` endpoint.

	This type has some additional attributes not existent in :class:`PublicUser`.

	country: str
		ISO-3166-1_ code of users country.
	email: str
		Email of user. Please do not this email is note necessarily verified by Spotify.
	product: str
		Users Spotify subscription level, could be ``free``, ``open`` or ``premium``. ``free`` and ``open`` are synonyms.
	'''

	def __init__(self, client, data):
		super().__init__(client, data)

		# this seems to have been removed from the api listing?
		#self.birthdate = data.pop('birthdate', None)

		self.country = data.pop('country', None)
		self.email = data.pop('email', None)
		self.product = data.pop('product', None)

	async def top_tracks(self, limit=None, offset=None, time_range=None):
		'''
		Gets the top tracks of the current user.

		Requires scope ``user-top-read``.

		:param int limit: How many tracks to return. Maximum is 50.
		:param int offset: The index of the first result to return.
		:param str time_range: The time period for which data are selected to form a top.

		Valid values for ``time_range``
		  - ``long_term`` (calculated from several years of data and including all new data as it becomes available),
		  - ``medium_term`` (approximately last 6 months),
		  - ``short_term`` (approximately last 4 weeks).

		:return: List[:class:`SimpleTrack`]
		'''

		return await self._client.get_me_top_tracks(limit=limit, offset=offset, time_range=time_range)

	async def top_artists(self, limit=None, offset=None, time_range=None):
		'''
		Get the top artists of the current user.

		:param int limit: How many artists to return. Maximum is 50.
		:param int offset: The index of the first result to return.
		:param str time_range: The time period for which data are selected to form a top.

		Valid values for ``time_range``
		  - ``long_term`` (calculated from several years of data and including all new data as it becomes available),
		  - ``medium_term`` (approximately last 6 months),
		  - ``short_term`` (approximately last 4 weeks).

		:return: List[:class:`SimpleArtist`]
		'''

		return await self._client.get_me_top_artists(limit=limit, offset=offset, time_range=time_range)

	async def create_playlist(self, name, public=False, collaborative=False, description=None):
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
			public=public,
			collaborative=collaborative,
			description=description
		)
