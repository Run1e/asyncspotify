
import asyncio, logging

from .object import Object
from .pager import Pager
from .playlist import FullPlaylist, SimplePlaylist
from .track import FullTrack, PlaylistTrack, SimpleTrack
from .artist import FullArtist
from .album import FullAlbum
from .user import PublicUser, PrivateUser

from .http import HTTP
from .deco import token, getids, check

from pprint import pprint


log = logging.getLogger(__name__)

class Client:
	
	_user = None
	
	def __init__(self, auth, session, cache=True):
		self.auth = auth
		self.cache = cache
		self.http = HTTP(session=session)
		self.http.set_access_token(self.auth.access_token)
		
	async def refresh_token(self):
		log.info('Refreshing tokens')
		await self.auth.refresh()
		self.http.set_access_token(self.auth.access_token)
	
	@token
	async def get_me(self):
		data = await self.http.get_me()
		self.user = PrivateUser(self, data)
	
	@getids
	@token
	async def create_playlist(self, user=None, name='Unnamed playlist', description=None, public=False, collaborative=False):
		data = await self.http.create_playlist(
			user_id=user or self.user.id,
			name=name,
			public=public,
			collaborative=collaborative,
			description=description
		)
		
		playlist = FullPlaylist(self, data)
		playlist._tracks = {}
		return playlist
	
	@token
	async def get_playlist(self, playlist_id):
		data = await self.http.get_playlist(playlist_id)
		playlist = FullPlaylist(self, data)
		await playlist._fill_tracks(PlaylistTrack, Pager(self.http, data.pop('tracks')))
		return playlist
	
	@getids
	@token
	async def get_user_playlists(self, user_id):
		data = await self.http.get_user_playlists(user_id)
		playlists = []
		async for playlist_data in Pager(self.http, data):
			playlist = SimplePlaylist(self, playlist_data)
			await playlist._fill_tracks(PlaylistTrack, Pager(self.http, await self.http.get_playlist_tracks(playlist.id)))
			playlists.append(playlist)
		return playlists
			
		
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
	async def get_user(self, user_id):
		data = await self.http.get_user(user_id)
		return PublicUser(self, data)
	
	@token
	async def get_track(self, track_id):
		data = await self.http.get_track(track_id)
		return FullTrack(self, data)
	
	@token
	async def get_tracks(self, *track_ids):
		if len(track_ids) > 50:
			raise ValueError('get_tracks track limit is 50.')
		data = await self.http.get_tracks(track_ids)
		tracks = []
		for track in data['tracks']:
			tracks.append(FullTrack(self, track))
		return tracks
	
	@token
	async def get_artist(self, artist_id):
		data = await self.http.get_artist(artist_id)
		return FullArtist(self, data)
	
	@token
	async def get_album(self, album_id):
		data = await self.http.get_album(album_id)
		album = FullAlbum(self, data)
		await album._fill_tracks(SimpleTrack, Pager(self.http, data['tracks']))
		return album
	
	@token
	async def get_albums(self, *album_ids):
		if len(album_ids) > 20:
			raise ValueError('get_albums album limit is 20.')
		data = await self.http.get_albums(album_ids)
		albums = []
		for album_obj in data['albums']:
			album = FullAlbum(self, album_obj)
			await album._fill_tracks(SimpleTrack, Pager(self.http, album_obj['tracks']))
			albums.append(album)
		return albums
		