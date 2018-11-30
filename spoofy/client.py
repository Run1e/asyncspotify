
import asyncio, aiohttp, logging

from .object import Object
from .pager import Pager, SearchPager
from .playlist import Playlist, FullPlaylist, SimplePlaylist
from .track import Track, FullTrack, PlaylistTrack, SimpleTrack
from .artist import Artist, FullArtist, SimpleArtist
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
	'''Client interface for the API.'''
	
	scopes = (
		'user-read-recently-played',
		'user-top-read',
		'user-follow-read',
		'user-follow-modify',
		'user-modify-playback-state',
		'user-read-playback-state',
		'user-read-currently-playing',
		'user-library-read',
		'user-library-modify',
		'user-read-private',
		'user-read-birthdate',
		'user-read-email',
		'playlist-modify-public',
		'playlist-read-collaborative',
		'playlist-modify-private',
		'playlist-read-private',
		'streaming',
		'app-remote-control'
	)
	
	def __init__(self, auth, session=None, loop=None):
		'''
		Creates a Spotify Client instance.
		
		:param auth: Instance of :class:`OAuth`
		:param session: Instance of `aiohttp.ClientSession <http://docs.aiohttp.org/en/stable/client_reference.html#aiohttp.ClientSession>`_
		:param loop: asyncio loop
		'''
		self.auth = auth
		if session is None:
			session = aiohttp.ClientSession(loop=loop or asyncio.get_event_loop())
		self.http = HTTP(session=session)
		self.http.set_access_token(self.auth.access_token)
	
	#@token
	async def refresh_token(self):
		'''Refresh the access and refresh tokens.'''
		
		log.info('Refreshing tokens')
		self.auth.refresh()
		self.http.set_access_token(self.auth.access_token)
		
	#@token
	async def search(self, *types, q=None, limit=10):
		'''
		Searches for tracks, artists, albums and/or playlists.
		
		:param types: The strings 'tracks', 'artists', 'albums' and/or 'playlist' - or you can pass the class equivalents.
		:param str q: The search query. See Spotifys query construction guide `here. <https://developer.spotify.com/documentation/web-api/reference/search/search/>`_
		:param int limit: How many results of each type to return.
		:return: A dict with a key for each type, whose values are a list of instances.
		'''
		
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
		
		data = await self.http.search(finished_types, q, limit=limit if limit < 50 else 50)
		
		results = {}
		for tpe in finished_types:
			results[tpe + 's'] = []
		
		if 'tracks' in results:
			async for track_obj in SearchPager(self.http, data, 'tracks', limit):
				results['tracks'].append(SimpleTrack(self, track_obj))
		if 'albums' in results:
			async for album_obj in SearchPager(self.http, data, 'albums', limit):
				results['albums'].append(SimpleAlbum(self, album_obj))
		if 'artists' in results:
			async for artist_obj in SearchPager(self.http, data, 'artists', limit):
				results['artists'].append(FullArtist(self, artist_obj))
		if 'playlists' in results:
			async for artist_obj in SearchPager(self.http, data, 'playlists', limit):
				results['playlists'].append(SimplePlaylist(self, artist_obj))
		
		return results
			
	async def search_tracks(self, q=None, limit=20):
		'''
		Alias for ``Client.search(spoofy.Track, ...)``
		
		:return: List[:class:`SimpleTrack`]
		'''
		
		results = await self.search(Track, q=q, limit=limit)
		return results['tracks']
	
	async def search_artists(self, q=None, limit=20):
		'''
		Alias for ``Client.search(spoofy.Artist, ...)``

		:return: List[:class:`SimpleArtist`]
		'''
		
		results = await self.search(Artist, q=q, limit=limit)
		return results['artists']
	
	async def search_albums(self, q=None, limit=20):
		'''
		Alias for ``Client.search(spoofy.Album, ...)``

		:return: List[:class:`SimpleAlbum`]
		'''
		
		results = await self.search(Album, q=q, limit=limit)
		return results['albums']
	
	async def search_playlists(self, q=None, limit=20):
		'''
		Alias for ``Client.search(spoofy.Playlist, ...)``

		:return: List[:class:`SimplePlaylist`]
		'''
		
		results = await self.search(Playlist, q=q, limit=limit)
		return results['playlists']
	
	#@token
	async def get_me(self):
		'''
		Gets the current user.
		
		:return: A :class:`PrivateUser` instance of the current user.
		'''
		
		data = await self.http.get_me()
		return PrivateUser(self, data)
	
	#@token
	async def get_me_top_tracks(self, limit=20, offset=0):
		'''
		Gets the top tracks of the current user.
		
		:param int limit: How many tracks to return. Maximum is 50.
		:param int offset: The index of the first result to return.
		:return: List[:class:`SimpleTrack`]
		'''
		
		if limit > 50:
			raise SpoofyException('Limit must be less or equal to 50.')
		
		data = await self.http.get_me_top_tracks(limit=limit, offset=offset)
		
		tracks = []
		for track_obj in data['items']:
			tracks.append(SimpleTrack(self, track_obj))
			
		return tracks
		
	#@token
	async def get_me_top_artists(self, limit=20, offset=0):
		'''
		Get the top artists of the current user.
		
		:param int limit: How many artists to return. Maximum is 50.
		:param int offset: The index of the first result to return.
		:return: List[:class:`SimpleArtist`]
		'''
		
		if limit > 50:
			raise SpoofyException('Limit must be less or equal to 50.')
		
		data = await self.http.get_me_top_artists(limit=limit, offset=offset)
		
		artists = []
		for artist_obj in data['items']:
			artists.append(SimpleArtist(self, artist_obj))
		
		return artists
		
	#@token
	async def get_user(self, user_id):
		'''
		Get a user.
		
		:param str user_id: Spotify ID of user.
		:return: A :class:`PublicUser` instance.
		'''
		
		try:
			data = await self.http.get_user(user_id)
		except NotFound:
			return None
		
		return PublicUser(self, data)
	
	#@token
	async def create_playlist(self, user, name='Unnamed playlist', description=None, public=False, collaborative=False):
		'''
		Create a new playlist.
		
		:param user: :class:`User` instance or user Spotify ID.
		:param str name: Name of the new playlist.
		:param str description: Description of the new playlist.
		:param bool public:
		:param bool collaborative:
		:return: An :class:`FullPlaylist` instance.
		'''
		
		data = await self.http.create_playlist(user, name, description, public, collaborative)
		
		playlist = FullPlaylist(self, data)
		playlist._tracks = {}
		
		return playlist
	
	#@getids
	#@token
	async def edit_playlist(self, playlist, name=None, description=None, public=None, collaborative=None):
		'''
		Edit a playlist.
		
		:param playlist: :class:`Playlist` instance or Spotify ID of playlist.
		:param str name: New name of the playlist.
		:param str description: New description of the playlist.
		:param bool public: New public state of the playlist.
		:param bool collaborative: New collaborative state of the playlist.
		'''
		
		await self.http.edit_playlist(
			playlist_id=playlist,
			name=name,
			description=description,
			public=public,
			collaborative=collaborative
		)
	
	#@token
	async def get_playlist(self, playlist_id):
		'''
		Get a pre-existing playlist.
		
		:param str playlist_id: Spotify ID of the playlist.
		:return: :class:`FullPlaylist` instance.
		'''
		
		try:
			data = await self.http.get_playlist(playlist_id)
		except NotFound:
			return None
		
		playlist = FullPlaylist(self, data)
		await playlist._fill_tracks(PlaylistTrack, Pager(self.http, data.pop('tracks')))
		
		return playlist
	
	#@getids
	#@token
	async def get_user_playlists(self, user):
		'''
		Get a list of attainable playlists a user owns.
		
		:param user: :class:`User` instance or users Spotify ID.
		:return: List[:class:`SimplePlaylist`]
		'''
		
		data = await self.http.get_user_playlists(user)
		
		playlists = []
		
		async for playlist_obj in Pager(self.http, data):
			if playlist_obj is None:
				playlists.append(None)
			else:
				playlist = SimplePlaylist(self, playlist_obj)
				await playlist._fill_tracks(PlaylistTrack, Pager(self.http, await self.http.get_playlist_tracks(playlist.id)))
				playlists.append(playlist)
		
		return playlists
	
	
	#@getids
	#@token
	async def playlist_add_tracks(self, playlist, tracks, position=0):
		'''
		Add tracks to a playlist.
		
		:param playlist: :class:`Playlist` or playlist Spotify ID.
		:param tracks: List of Spotify IDs or :class:`Track`.
		:param int position: Position in the playlist to insert tracks.
		'''
		
		tracks_fin = []
		
		for index, track in enumerate(tracks):
			if isinstance(track, Object):
				track = track.id
			if not track.startswith('spotify:track:'):
				track = 'spotify:track:' + track
			tracks_fin.append(track)
			
		for slice in SliceIterator(tracks_fin, 100):
			await self.http.playlist_add_tracks(playlist, slice, position=position)
	
	#@token
	async def get_track(self, track_id):
		'''
		Get a track.
		
		:param str track_id: Spotify ID of track.
		:return: :class:`FullTrack` instance.
		'''
		
		try:
			data = await self.http.get_track(track_id)
		except NotFound:
			return None
		
		return FullTrack(self, data)
	
	#@token
	async def get_tracks(self, *track_ids):
		'''
		Get several tracks.
		
		:param str track_ids: List of track Spotify IDs
		:return: List[:class:`FullTrack`]
		'''
		
		tracks = []
		
		for slice in SliceIterator(track_ids, 50):
			data = await self.http.get_tracks(slice)
			
			for track_obj in data['tracks']:
				if track_obj is None:
					tracks.append(None)
				else:
					tracks.append(FullTrack(self, track_obj))
		
		return tracks
	
	#@getids
	#@token
	async def get_audio_features(self, track):
		'''
		Get 'Audio Features' of a track.
		
		:param track: :class:`Track` instance or Spotify ID of track.
		:return: :class:`AudioFeatures`
		'''
		
		try:
			data = await self.http.get_audio_features(track)
		except NotFound:
			return None
		
		return AudioFeatures(self, data)
	
	#@token
	async def get_artist(self, artist_id):
		'''
		Get an artist.
		
		:param str artist_id: Spotify ID of artist.
		:return: :class:`FullArtist` instance.
		'''
		
		try:
			data = await self.http.get_artist(artist_id)
		except NotFound:
			return None
		
		return FullArtist(self, data)
	
	#@token
	async def get_artists(self, *artist_ids):
		'''
		Get several artists.
		
		:param artist_ids: List of artist Spotify IDs.
		:return: List[:class:`FullArtist`]
		'''
		
		artists = []
		
		for slice in SliceIterator(artist_ids, 50):
			data = await self.http.get_artists(slice)
			
			for artist_obj in data['artists']:
				if artist_obj is None:
					artists.append(None)
				else:
					artists.append(FullArtist(self, artist_obj))
		
		return artists
	
	
	#@token
	async def get_album(self, album_id):
		'''
		Get an album.
		
		:param str album_id: Spotify ID of album.
		:return: :class:`FullAlbum` instance.
		'''
		
		try:
			data = await self.http.get_album(album_id)
		except NotFound:
			return None
		
		album = FullAlbum(self, data)
		await album._fill_tracks(SimpleTrack, Pager(self.http, data['tracks']))
		
		return album
	
	#@token
	async def get_albums(self, *album_ids):
		'''
		Get several albums.
		
		:param str album_ids: Spotify ID of album.
		:return: List[:class:`FullAlbum`]
		'''
		
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
	
	#@getids
	#@token
	async def get_album_tracks(self, album):
		'''
		Get tracks from an album.
		
		:param album: :class:`Album` or Spotify ID of album.
		:return: List[:class:`SimpleTrack`]
		'''
		
		data = await self.http.get_album_tracks(album)
		
		tracks = []
		
		async for track_obj in Pager(self.http, data):
			tracks.append(SimpleTrack(self, track_obj))
			
		return tracks