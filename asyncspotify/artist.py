from .mixins import ExternalURLMixin, ImageMixin
from .object import Object


class _BaseArtist(Object, ExternalURLMixin):
	_type = 'artist'

	def __init__(self, client, data):
		super().__init__(client, data)

		self._fill_external_urls(data.pop('external_urls'))

	async def top_tracks(self, market='from_token'):
		'''
		Returns this artists top tracks.

		:param market: Market to find tracks for.
		:return: List[:class:`FullTrack`]
		'''

		return await self._client.get_artist_top_tracks(self.id, market=market)

	async def related_artists(self):
		'''
		Get related artists. Maximum of 20 artists.

		:return: List[:class:`FullArtist`]
		'''

		return await self._client.get_artist_related_artists(self.id)

	async def albums(self, include_groups=None, country=None, limit=None, offset=None):
		'''
		Get artist' albums

		:return: List[:class:`SimpleAlbum`]
		'''

		return await self._client.get_artist_albums(
			self.id,
			include_groups=include_groups,
			country=country,
			limit=limit,
			offset=offset
		)


class SimpleArtist(_BaseArtist):
	'''
	Represents an Artist object.

	id: str
		Spotify ID of the artist.
	name: str
		Name of the artist.
	uri: str
		Spotify URI of the artist.
	link: str
		Spotify URL of the artist.
	external_urls: dict
		Dictionary that maps type to url.
	'''


class FullArtist(_BaseArtist, ImageMixin):
	'''
	Represents a complete Artist object.
	
	This type has some additional attributes not existent in :class:`SimpleArtist`.
	
	follow_count: int
		Follow count of the artist.
	genres: List[str]
		Genres associated with the artist.
	popularity: int
		An indicator of the popularity of the track, 0 being least popular and 100 being the most.
	images: List[:class:`Image`]
		List of associated images.
	'''

	def __init__(self, client, data):
		super().__init__(client, data)

		self.follower_count = data['followers']['total']
		self.genres = data.pop('genres')
		self.popularity = data.pop('popularity')

		self._fill_images(data.pop('images'))
