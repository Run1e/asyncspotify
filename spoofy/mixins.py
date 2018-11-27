
from .image import Image
from .deco import getids

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
			
class TrackMixin:
	@property
	def tracks(self):
		return list(self._tracks.values())
	
	@getids
	@property
	def has_track(self, track):
		return track in self._tracks
		
	
	async def _fill_tracks(self, object_type, pager):
		self._tracks = {}
		async for object in pager:
			trck = object_type(**object)
			trck.playlist = self
			self._tracks[trck.id] = trck