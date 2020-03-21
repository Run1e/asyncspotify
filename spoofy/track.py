from datetime import datetime, timedelta

from .album import SimpleAlbum
from .mixins import ArtistMixin, ExternalIDMixin, ExternalURLMixin
from .object import Object


class _BaseTrack(Object, ExternalURLMixin, ArtistMixin):
	_type = 'track'

	def __init__(self, client, data):
		super().__init__(client, data)

		self.available_markets = data.pop('available_markets', None)
		self.disc_number = data.pop('disc_number')
		self.explicit = data.pop('explicit')
		self.preview_url = data.pop('preview_url')
		self.track_number = data.pop('track_number')
		self.is_local = data.pop('is_local')

		self.duration = timedelta(milliseconds=data.pop('duration_ms'))

		self._fill_external_urls(data.pop('external_urls'))
		self._fill_artists(data.pop('artists'))

	def avaliable_in(self, market):
		return market in self.available_markets

	async def get_features(self):
		'''
		Get 'Audio Features' of the track.
		
		:param track: :class:`Track` instance or Spotify ID of track.
		:return: :class:`AudioFeatures`
		'''

		return await self._client.get_audio_features(self.id)


class SimpleTrack(_BaseTrack):
	'''
	Represents a Track object.

	id: str
		Spotify ID of the track.
	name: str
		Name of the track.
	artists: List[:class:`Artist`]
		List of artists that appear on the track.
	images: List[:class:`Image`]
		List of associated images, such as album cover in different sizes.
	uri: str
		Spotify URI of the album.
	link: str
		Spotify URL of the album.
	type: str
		Plaintext string of object type: ``track``.
	available_markets: List[str] or None
		Markets where the album is available: `ISO_3166-1 <https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2>`_.
	disc_number: int
		What disc the track appears on. Usually ``1`` unless there are several discs in the album.
	duration: `timedelta <https://docs.python.org/3/library/datetime.html#timedelta-objects>`_
		timedelta instance representing the length of the track.
	explicit: bool
		Whether the track is explicit or not.
	external_urls: dict
		Dictionary that maps type to url.
	is_playable: bool
		tbc
	linked_from: :class:`LinkedTrack`
		tbc
	restrictions: restrictions object
		tbc
	preview_url: str
		An URL to a 30 second preview (MP3) of the track.
	track_number: int
		The number of the track on the album.
	is_local: bool
		Whether the track is from a local file.
	'''


class FullTrack(_BaseTrack, ExternalIDMixin):
	'''
	Represents a complete Track object.
	
	This type has some additional attributes not existent in :class:`SimpleTrack`.
	
	album: :class:`SimpleAlbum`
		An instance of the album the track appears on.
	popularity: int
		An indicator of the popularity of the track, 0 being least popular and 100 being the most.
	external_ids: dict
		Dictionary of external IDs.
	'''

	def __init__(self, client, data):
		super().__init__(client, data)

		self.popularity = data.pop('popularity')
		self._fill_external_ids(data.pop('external_ids'))

		self.album = SimpleAlbum(client, data.pop('album'))


class PlaylistTrack(FullTrack):
	'''
	Represents a Track object originating from a playlist.
	
	This type has some additional attributes not existent in :class:`SimpleTrack` or :class:`FullTrack`.
	
	added_at: `datetime <https://docs.python.org/3/library/datetime.html#module-datetime>`_
		Indicates when the track was added to the playlist.
	added_by: User object
		Indicates who added the track to the playlist. The information provided from the API is not enough to instantiate a PublicUser object, so it's a plain copy of the returned json object.
	'''

	def __init__(self, client, data):
		super().__init__(client, data.pop('track'))
		self.added_at = datetime.strptime(data.pop('added_at'), "%Y-%m-%dT%H:%M:%SZ")
		self.added_by = data.pop('added_by')
