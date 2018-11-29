
from .object import Object
from .mixins import ImageMixin, ExternalURLMixin

class Artist(Object, ExternalURLMixin):
	
	_type = 'artist'
	
	def __init__(self, client, data):
		super().__init__(client, data)
		
		self._fill_external_urls(data.pop('external_urls'))

class SimpleArtist(Artist):
	pass

class FullArtist(Artist, ImageMixin):
	
	def __init__(self, client, data):
		super().__init__(client, data)
		
		self.follower_count = data['followers']['total']
		self.genres = data.pop('genres')
		self.popularity = data.pop('popularity')
		
		self._fill_images(data.pop('images'))
		