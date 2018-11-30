
import asyncio, aiohttp, logging

from .object import Object
from .pager import Pager, SearchPager
from .playlist import Playlist, FullPlaylist, SimplePlaylist
from .track import Track, FullTrack, PlaylistTrack, SimpleTrack
from .artist import Artist, FullArtist
from .album import Album, FullAlbum, SimpleAlbum
from .user import PublicUser, PrivateUser
from .features import AudioFeatures
from .exceptions import SpoofyException, NotFound
from .utils import SliceIterator

from .http import HTTP
from .deco import token, getids

from pprint import pprint

log = logging.getLogger(__name__)

class Client:
	
	def __init__(self, auth, session=None, loop=None):
		self.auth = auth
		if session is None:
			session = aiohttp.ClientSession(loop=loop or asyncio.get_event_loop())
		self.http = HTTP(session=session)
		self.http.set_access_token(self.auth.access_token)
	
	async def refresh_token(self):
		log.info('Refreshing tokens')
		await self.auth.refresh()
		self.http.set_access_token(self.auth.access_token)
	
	@token
	async def search(self, *types, q=None, total=10):
		if q is None:
			raise SpoofyException('Search query required.')
		
		finished_types = []
		for tpe in types:
			if hasattr(tpe, '_type') and issubclass(tpe, Object):
				finished_types.append(tpe._type)
			elif isinstance(tpe, str):
				finished_types.append(tpe)
			else:
				raise SpoofyException('Unknown type.')
		
		data = await self.http.search(finished_types, q, limit=total if total < 50 else 50)
		
		results = {}
		for tpe in finished_types:
			results[tpe + 's'] = []
		
		if 'tracks' in results:
			async for track_obj in SearchPager(self.http, data, 'tracks', total):
				results['tracks'].append(SimpleTrack(self, track_obj))
		if 'albums' in results:
			async for album_obj in SearchPager(self.http, data, 'albums', total):
				results['albums'].append(SimpleAlbum(self, album_obj))
		if 'artists' in results:
			async for artist_obj in SearchPager(self.http, data, 'artists', total):
				results['artists'].append(FullArtist(self, artist_obj))
		if 'playlists' in results:
			async for artist_obj in SearchPager(self.http, data, 'playlists', total):
				results['playlists'].append(SimplePlaylist(self, artist_obj))
		
		return results
			
	async def search_tracks(self, q=None, total=20):
		results = await self.search(Track, q=q, total=total)
		return results['tracks']
	
	async def search_artists(self, q=None, total=20):
		results = await self.search(Artist, q=q, total=total)
		return results['artists']
	
	async def search_albums(self, q=None, total=20):
		results = await self.search(Album, q=q, total=total)
		return results['albums']
	
	async def search_playlists(self, q=None, total=20):
		results = await self.search(Playlist, q=q, total=total)
		return results['playlists']
	
	@token
	async def get_me(self):
		data = await self.http.get_me()
		return PrivateUser(self, data)
	
	@token
	async def get_user(self, user_id):
		try:
			data = await self.http.get_user(user_id)
		except NotFound:
			return None
		
		return PublicUser(self, data)
	
	@getids
	@token
	async def create_playlist(self, user, name='Unnamed playlist', description=None, public=False, collaborative=False):
		data = await self.http.create_playlist(user or self.user.id, name, description, public, collaborative)
		
		playlist = FullPlaylist(self, data)
		playlist._tracks = {}
		
		return playlist
	
	@token
	async def get_playlist(self, playlist_id):
		
		try:
			data = await self.http.get_playlist(playlist_id)
		except NotFound:
			return None
		
		playlist = FullPlaylist(self, data)
		await playlist._fill_tracks(PlaylistTrack, Pager(self.http, data.pop('tracks')))
		
		return playlist
	
	@getids
	@token
	async def get_user_playlists(self, user_id):
		data = await self.http.get_user_playlists(user_id)
		
		playlists = []
		
		async for playlist_obj in Pager(self.http, data):
			if playlist_obj is None:
				playlists.append(None)
			else:
				playlist = SimplePlaylist(self, playlist_obj)
				await playlist._fill_tracks(PlaylistTrack, Pager(self.http, await self.http.get_playlist_tracks(playlist.id)))
				playlists.append(playlist)
		
		return playlists
	
	
	@getids
	@token
	async def playlist_add_tracks(self, playlist_id, track_ids, position=0):
		
		tracks = []
		
		for index, track in enumerate(track_ids):
			if isinstance(track, Object):
				track = track.id
			if not track.startswith('spotify:track:'):
				track = 'spotify:track:' + track
			tracks.append(track)
			
		for slice in SliceIterator(tracks, 100):
			await self.http.playlist_add_tracks(playlist_id, slice, position=position)
	
	@token
	async def get_track(self, track_id):
		try:
			data = await self.http.get_track(track_id)
		except NotFound:
			return None
		
		return FullTrack(self, data)
	
	@token
	async def get_tracks(self, *track_ids):
		tracks = []
		
		for slice in SliceIterator(track_ids, 50):
			data = await self.http.get_tracks(slice)
			
			for track_obj in data['tracks']:
				if track_obj is None:
					tracks.append(None)
				else:
					tracks.append(FullTrack(self, track_obj))
		
		return tracks
	
	@getids
	@token
	async def get_audio_features(self, track_id):
		try:
			data = await self.http.get_audio_features(track_id)
		except NotFound:
			return None
		
		return AudioFeatures(self, data)
	
	@token
	async def get_artist(self, artist_id):
		try:
			data = await self.http.get_artist(artist_id)
		except NotFound:
			return None
		
		return FullArtist(self, data)
	
	@token
	async def get_artists(self, *artist_ids):
		
		artists = []
		
		for slice in SliceIterator(artist_ids, 50):
			data = await self.http.get_artists(slice)
			
			for artist_obj in data['artists']:
				if artist_obj is None:
					artists.append(None)
				else:
					artists.append(FullArtist(self, artist_obj))
		
		return artists
	
	
	@token
	async def get_album(self, album_id):
		try:
			data = await self.http.get_album(album_id)
		except NotFound:
			return None
		
		album = FullAlbum(self, data)
		await album._fill_tracks(SimpleTrack, Pager(self.http, data['tracks']))
		
		return album
	
	@token
	async def get_albums(self, *album_ids):
		if len(album_ids) > 20:
			raise SpoofyException('get_albums album limit is 20.')
		
		data = await self.http.get_albums(album_ids)
		
		albums = []
		
		for album_obj in data['albums']:
			if album_obj is None:
				albums.append(None)
			else:
				album = FullAlbum(self, album_obj)
				await album._fill_tracks(SimpleTrack, Pager(self.http, album_obj['tracks']))
				albums.append(album)
		
		return albums
		