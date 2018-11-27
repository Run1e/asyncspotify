
from datetime import datetime

from .object import Object
from .mixins import ExternalURLMixin, TrackMixin, ImageMixin, ArtistMixin, ExternalIDMixin

class Album(Object, ExternalURLMixin, TrackMixin, ImageMixin, ArtistMixin):
	
	__date_fmt = dict(year='%Y', month='%Y-%m', day='%Y-%m-%d')
	
	def __init__(self, data):
		super().__init__(data)
		
		self.album_group = data.pop('album_group', None) # could be non-existent
		self.album_type = data.pop('album_type')
		self.available_markets = data.pop('available_markets')
		
		self.release_date_precision = data.pop('release_date_precision')
		self.release_date = datetime.strptime(
			data.pop('release_date'),
			self.__date_fmt[self.release_date_precision]
		)
		
		self._fill_external_urls(data.pop('external_urls'))
		self._fill_artists(data.pop('artists'))
		self._fill_images(data.pop('images'))

class SimpleAlbum(Album):
	pass

class FullAlbum(Album, ExternalIDMixin):
	
	def __init__(self, data):
		super().__init__(data)
		
		self.genres = data.pop('genres')
		self.label = data.pop('label')
		self.popularity = data.pop('popularity')
		self.copyrights = data.pop('copyrights')
		
		self._fill_external_ids(data.pop('external_ids'))
		