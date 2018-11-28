
from datetime import datetime, timedelta

from .object import Object
from .album import SimpleAlbum
from .mixins import ExternalURLMixin, ArtistMixin, ExternalIDMixin

from pprint import pprint

class Track(Object, ExternalURLMixin, ArtistMixin):
	
	def __init__(self, client, data):
		super().__init__(client, data)
		
		self.available_markets = data.pop('available_markets')
		self.disc_number = data.pop('disc_number')
		self.explicit = data.pop('explicit')
		self.preview_url = data.pop('preview_url')
		self.track_number = data.pop('track_number')
		self.is_local = data.pop('is_local')
		
		self.length = timedelta(milliseconds=data.pop('duration_ms'))
		
		self._fill_external_urls(data.pop('external_urls'))
		self._fill_artists(data.pop('artists'))
	
	def avaliable_in(self, market):
		return market in self.available_markets

class SimpleTrack(Track):
	pass
		
class FullTrack(Track, ExternalIDMixin):
	
	def __init__(self, client, data):
		super().__init__(client, data)
		
		self.popularity = data.pop('popularity')
		self._fill_external_ids(data.pop('external_ids'))
		
		self.album = SimpleAlbum(client, data.pop('album'))
		

class PlaylistTrack(FullTrack):
	
	def __init__(self, client, data):
		super().__init__(client, data.pop('track'))
		self.added_at = datetime.strptime(data.pop('added_at'), "%Y-%m-%dT%H:%M:%SZ")
		self.added_by = data.pop('added_by')
