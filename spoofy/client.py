
import asyncio, logging

from .pager import Pager
from .playlist import Playlist, SimplePlaylist
from .track import Track, SimpleArtist
from .artist import Artist, SimpleArtist

from .http import HTTP
from .exceptions import Unauthorized

log = logging.getLogger(__name__)

def token(method):
	async def predicate(self, *args, **kwargs):
		try:
			return await method(self, *args, **kwargs)
		except Unauthorized as exc:
			if exc.message == 'The access token expired':
				await self.refresh_token()
				return await method(self, *args, **kwargs)
			else:
				raise
	return predicate
	

class Client:
	
	def __init__(self, auth, session):
		self.auth = auth
		self.http = HTTP(session=session)
		self.http.set_access_token(self.auth.access_token)
		
	async def refresh_token(self):
		await self.auth.refresh()
		self.http.set_access_token(self.auth.access_token)
	
	@token
	async def get_playlist(self, playlist_id):
		obj = await self.http.get_playlist(playlist_id)
		pl = Playlist(**obj)
		await pl._fill_tracks(Pager(self.http, obj['tracks']))
		return pl
	
	@token
	async def get_track(self, track_id):
		obj = await self.http.get_track(track_id)
		return Track(**obj)