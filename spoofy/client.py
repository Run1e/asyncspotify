
import asyncio, json

from .playlist import Playlist

from .http import HTTP
from .exceptions import NoCredentialsFound

class Client:
	def __init__(self, access_token=None, refresh_token=None, on_refresh=None):
		
		self._access_token = access_token
		self._refresh_token = refresh_token
		self.on_refresh = on_refresh
		
		self.http = HTTP(self)
		
	@property
	def access_token(self):
		return self._access_token
	
	@property
	def refresh_token(self):
		return self._refresh_token

	async def get_playlist(self, playlist_id):
		obj = await self.http.get_playlist(playlist_id)
		return Playlist(obj)