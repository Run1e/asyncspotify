
import asyncio, logging

from .pager import Pager
from .playlist import FullPlaylist
from .track import FullTrack
from .artist import FullArtist
from .album import FullAlbum

from .http import HTTP
from .exceptions import Unauthorized

from pprint import pprint


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
		playlist = FullPlaylist(**obj)
		await playlist._fill_tracks(Pager(self.http, obj['tracks']))
		return playlist
	
	@token
	async def get_track(self, track_id):
		obj = await self.http.get_track(track_id)
		return FullTrack(**obj)
	
	@token
	async def get_tracks(self, *track_ids):
		if len(track_ids) > 50:
			raise ValueError('get_tracks track limit is 50.')
		obj = await self.http.get_tracks(track_ids)
		tracks = []
		for track in obj['tracks']:
			tracks.append(FullTrack(**track))
		return tracks
	
	@token
	async def get_artist(self, artist_id):
		obj = await self.http.get_artist(artist_id)
		return FullArtist(**obj)
	
	@token
	async def get_album(self, album_id):
		obj = await self.http.get_album(album_id)
		album = FullAlbum(**obj)
		await album._fill_tracks(Pager(self.http, obj['tracks']))
		return album