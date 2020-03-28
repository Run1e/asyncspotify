import logging

from .http import Route
from .image import Image
from .object import SpotifyObject
from .pager import Pager

log = logging.getLogger(__name__)


class ArtistMixin:
	def __init__(self, data):
		from .artist import SimpleArtist

		artists = data.pop('artists')
		self.artists = []

		for art in artists:
			self.artists.append(SimpleArtist(self._client, art))


class ImageMixin:
	def __init__(self, data):
		images = data.pop('images', None)
		self.images = []

		if images is not None:
			for img in images:
				self.images.append(Image(img))


class ExternalIDMixin:
	def __init__(self, data):
		external_ids = data.pop('external_ids')
		self.external_ids = {}

		for key, value in external_ids.items():
			self.external_ids[key] = value


class ExternalURLMixin:
	def __init__(self, data):
		external_urls = data.pop('external_urls')
		self.external_urls = {}

		self.link = external_urls.get('spotify', None)
		for site, url in external_urls.items():
			self.external_urls[site] = url


def valid_item(item):
	if item is None:
		return False
	# maybe explicitly check for self._track_class?
	if 'track' in item and item['track'] is None:
		return False
	return True


class TrackMixin:
	def __init__(self, data):
		tracks = data.pop('tracks', None)
		if tracks is None:
			return

		items = tracks.pop('items', None)
		if items is None:
			return

		self.tracks = []

		for item in items:
			if valid_item(item):
				self._add_track(item)

		self.__total = tracks.get('total')
		self.__limit = tracks.get('limit')

		self.track_count = self.__total

	async def __aiter__(self):
		'''Create a pager and iterate all tracks in this object. Also updates the ``tracks`` cache.'''

		self.tracks = []

		# get new pager
		r = Route('GET', '{0}s/{1}/tracks'.format(self._type, self.id), offset=0, limit=self.__limit)
		pager_data = await self._client.http.request(r)

		self.__total = pager_data.get('total')
		self.track_count = self.__total

		async for item in Pager(self._client.http, pager_data):
			if valid_item(item):
				yield self._add_track(item)
			else:
				# if it's not a valid item it shouldn't count towards the total track count goal
				self.__total -= 1

	async def fill(self):
		'''Update this objects ``tracks`` cache.'''

		async for track in self:
			pass

	def is_filled(self):
		'''Whether this object contains as many tracks as advertised by the previous pager.'''

		return len(self.tracks) >= self.__total

	def has_track(self, track):
		'''Check if this object has a track.'''

		if isinstance(track, SpotifyObject):
			track = track.id
		return any(track == t.id for t in self.tracks)

	def _add_track(self, track_data):
		track = self._track_class(self._client.http, track_data)
		self.tracks.append(track)
		return track
