
from .image import Image

class ArtistMixin:
	def _fill_artists(self, artists):
		from .artist import SimpleArtist
		
		self.artists = []
		for art in artists:
			self.artists.append(SimpleArtist(**art))

class ImageMixin:
	def _fill_images(self, images):
		self.images = []
		for img in images:
			self.images.append(Image(**img))
			

class UrlMixin:
	def _fill_urls(self, external_urls):
		self.link = external_urls.pop('spotify', None)
		
		self.urls = {}
		for site, url in external_urls.items():
			self.urls[site] = url
			
class TrackContainerMixin:
	async def _fill_tracks(self, object_type, pager):
		self.tracks = []
		async for object in pager:
			trck = object_type(**object)
			trck.playlist = self
			self.tracks.append(trck)