import logging

from .image import Image
from .object import SpotifyObject

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


class TrackMixin:
	@property
	def has_track(self, track):
		if isinstance(track, SpotifyObject):
			track = track.id
		return any(track == t.id for t in self.tracks)

	async def _fill_tracks(self, object_type, pager):
		self.tracks = []

		async for obj in pager:
			# TODO: handle this case nicer?
			if obj.get('track', True) is None:
				log.warning('Object has no track associated with it: %s', obj)
				continue

			self.tracks.append(object_type(self._client, obj))
