
import asyncio, logging

from .object import Object
from .pager import Pager
from .playlist import FullPlaylist
from .track import FullTrack, PlaylistTrack, SimpleTrack
from .artist import FullArtist
from .album import FullAlbum

from .http import HTTP
from .deco import token, getids

from pprint import pprint


log = logging.getLogger(__name__)

class Client:
	
	def __init__(self, auth, session, on_refresh=None):
		self.auth = auth
		self.http = HTTP(session=session)
		self.http.set_access_token(self.auth.access_token)
		self.on_refresh = on_refresh
		
	async def refresh_token(self):
		log.info('Refreshing tokens')
		await self.auth.refresh()
		self.http.set_access_token(self.auth.access_token)
		
		if self.on_refresh:
			log.info('Calling on_refresh hook')
			self.on_refresh(self.auth.access_token, self.auth.refresh_token)
	
	@token
	async def get_playlist(self, playlist_id):
		obj = await self.http.get_playlist(playlist_id)
		playlist = FullPlaylist(**obj)
		playlist._fill_events(self)
		await playlist._fill_tracks(PlaylistTrack, Pager(self.http, obj['tracks']))
		return playlist
	
	@getids
	@token
	async def _playlist_add_tracks(self, playlist_id, track_ids, position=0):
		tracks = []
		for index, track in enumerate(track_ids):
			if isinstance(track, Object):
				track = track.id
			if not track.startswith('spotify:track:'):
				track = 'spotify:track:' + track
			tracks.append(track)
		await self.http.playlist_add_tracks(playlist_id, tracks, position=position)
	
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
		await album._fill_tracks(SimpleTrack, Pager(self.http, obj['tracks']))
		return album