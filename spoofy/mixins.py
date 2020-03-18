from .image import Image
from .object import Object


class ArtistMixin:
	def _fill_artists(self, artists):
		from .artist import SimpleArtist

		self.artists = []

		for art in artists:
			self.artists.append(SimpleArtist(self._client, art))


class ImageMixin:
	def _fill_images(self, images):
		self.images = []

		for img in images:
			self.images.append(Image(img))


class ExternalIDMixin:
	def _fill_external_ids(self, external_ids):
		self.external_ids = {}
		for key, value in external_ids.items():
			self.external_ids[key] = value


class ExternalURLMixin:
	def _fill_external_urls(self, external_urls):
		self.urls = {}

		self.link = external_urls.pop('spotify', None)
		for site, url in external_urls.items():
			self.urls[site] = url


class TrackMixin:

	@property
	def has_track(self, track):
		if isinstance(track, Object):
			track = track.id
		return any(track == t.id for t in self.tracks)

	async def _fill_tracks(self, object_type, pager):
		self.tracks = []

		async for object in pager:
			# TODO: handle this case nicer?
			if object['track'] is not None:
				self.tracks.append(object_type(self._client, object))


class UserMixin:
	async def _get_user(self):
		pass
