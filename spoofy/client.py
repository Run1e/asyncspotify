import asyncio, logging
from datetime import timedelta

from .object import Object
from .playlist import Playlist, FullPlaylist, SimplePlaylist
from .track import Track, FullTrack, PlaylistTrack, SimpleTrack
from .artist import Artist, FullArtist, SimpleArtist
from .album import Album, FullAlbum, SimpleAlbum
from .user import PublicUser, PrivateUser

from .device import Device
from .playing import CurrentlyPlaying, CurrentlyPlayingContext
from .audiofeatures import AudioFeatures

from .pager import Pager, SearchPager, CursorBasedPaging
from .exceptions import SpoofyException, NotFound
from .utils import SliceIterator

from .http import HTTP

from pprint import pprint

log = logging.getLogger(__name__)


class Client:
	'''
	Client interface for the API.

	This is the class you should be interfacing with when fetching Spotify objects.

	auth: :class:`OAuth`
		OAuth instance used for authenticating with the API.
	session: `aiohttp.ClientSession <http://docs.aiohttp.org/en/stable/client_reference.html#aiohttp.ClientSession>`_
		ClientSession used for HTTP requests.
	'''

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

	def __init__(self, auth):
		'''
		Creates a Spotify Client instance.

		:param auth: Instance of :class:`OAuth`
		'''

		self.auth = auth
		self.http = HTTP(auth)

	async def __aenter__(self):
		return self

	async def __aexit__(self, exc_type, exc_val, exc_tb):
		await self.close_session()

	def _get_id(self, obj):
		if isinstance(obj, Object):
			return obj.id
		else:
			return obj

	async def refresh_token(self):
		'''Refresh the access and refresh tokens.'''

		log.info('Refreshing tokens')
		self.auth.refresh()

	async def get_player(self, **kwargs):
		'''
		Get a context for what user is currently playing.

		:param kwargs: query params for this request
		:return: :class:`PlayingContext`
		'''

		data = await self.http.get_player(**kwargs)

		return CurrentlyPlayingContext(self, data)

	async def player_currently_playing(self, **kwargs):
		data = await self.http.player_currently_playing(**kwargs)

		return CurrentlyPlaying(self, data)

	async def get_devices(self):
		'''
		Get a list of user devices.

		:return: A list of maximum 20 devices.
		'''

		data = await self.http.get_devices()

		devices = []

		for device_obj in data['devices']:
			devices.append(Device(self, device_obj))

		return devices

	async def player_next(self, device=None):
		'''
		Skip to the next track in a player.

		:param device: :class:`Device` or Spotify ID.
		'''

		await self.http.player_next(device_id=self._get_id(device))

	async def player_prev(self, device=None):
		'''
		Play the previous track.

		:param device: :class:`Device` or Spotify ID.
		'''

		await self.http.player_prev(device_id=self._get_id(device))

	async def player_play(self, device=None, **kwargs):
		'''
		Start playback on device.

		:param device: :class:`Device` or Spotify ID.
		:param kwargs: body params of the request. For example:
		player_play(context_uri='spotify:album:6xKK037rfCf2f6gf30SpvL',
					offset=dict(uri='spotify:track:2beor6qrB0XJxW1CM6X9x2'), position_ms=98500)
		'''

		await self.http.player_play(device_id=self._get_id(device), **kwargs)

	async def player_pause(self, device=None):
		'''
		Stop playback on a device.

		:param device: :class:`Device` or Spotify ID.
		'''

		await self.http.player_pause(device_id=self._get_id(device))

	async def player_seek(self, time, device=None):
		'''
		Seek to a point in the currently playing track.

		:param time: timedelta object or milliseconds (integer)
		:param device: :class:`Device` or Spotify ID.
		'''

		if isinstance(time, timedelta):
			time = time.days * (1000*60*60*24) + time.seconds * 1000 + time.microseconds // 1000
		await self.http.player_seek(time, self._get_id(device))

	async def player_repeat(self, state, device=None):
		'''
		Set player repeat mode.

		:param str state: Can be 'track', 'context' or 'off'.
		:param device: :class:`Device` or Spotify ID.
		'''

		await self.http.player_repeat(state, self._get_id(device))

	async def player_volume(self, volume, device=None):
		'''
		Set player volume.

		:param int volume: Value from 0 to 100.
		:param device: :class:`Device` or Spotify ID.
		'''

		await self.http.player_volume(volume, self._get_id(device))

	async def player_shuffle(self, state, device=None):
		'''
		Set player shuffle mode.

		:param bool state: Shuffle mode state.
		:param device: :class:`Device` or Spotify ID.
		'''

		await self.http.player_shuffle(state, self._get_id(device))

	async def search(self, *types, q, limit=10, **kwargs):
		'''
		Searches for tracks, artists, albums and/or playlists.

		:param types: The strings 'tracks', 'artists', 'albums' and/or 'playlist' - or you can pass the class equivalents.
		:param str q: The search query. See Spotifys query construction guide `here. <https://developer.spotify.com/documentation/web-api/reference/search/search/>`_
		:param int limit: How many results of each type to return.
		:param kwargs: other query params for this method
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

		data = await self.http.search(finished_types, q, limit=limit if limit < 50 else 50, **kwargs)

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

	async def search_albums(self, q=None, limit=20, **kwargs):
		'''
		Alias for ``Client.search(spoofy.Album, ...)``

		:return: List[:class:`SimpleAlbum`]
		'''

		results = await self.search(Album, q=q, limit=limit, **kwargs)
		return results['albums']

	async def search_playlists(self, q=None, limit=20):
		'''
		Alias for ``Client.search(spoofy.Playlist, ...)``

		:return: List[:class:`SimplePlaylist`]
		'''

		results = await self.search(Playlist, q=q, limit=limit)
		return results['playlists']

	async def search_track(self, q=None):
		'''
		Returns the top track for the query.

		:return: :class:`SimpleTrack` or None
		'''

		return (await self.search_tracks(q=q, limit=1))[0]

	async def search_artist(self, q=None):
		'''
		Returns the top artist for the query.

		:return: :class:`SimpleArtist` or None
		'''

		return (await self.search_artists(q=q, limit=1))[0]

	async def search_album(self, q=None):
		'''
		Returns the top album for the query.

		:return: :class:`SimpleAlbum`
		'''

		return (await self.search_albums(q=q, limit=1))[0]

	async def search_playlist(self, q=None):
		'''
		Returns the top playlist for the query.

		:return: :class:`SimplePlaylist`
		'''

		return (await self.search_playlists(q=q, limit=1))[0]

	async def get_me(self):
		'''
		Gets the current user.

		:return: A :class:`PrivateUser` instance of the current user.
		'''

		data = await self.http.get_me()
		return PrivateUser(self, data)

	async def get_me_top_tracks(self, limit=20, offset=0, time_range='medium_term'):
		'''
		Gets the top tracks of the current user.

		Requires scope ``user-top-read``.

		:param int limit: How many tracks to return. Maximum is 50.
		:param int offset: The index of the first result to return.
		:param str time_range: The time period for which data are selected to form a top. Valid values:
		- long_term (calculated from several years of data and including all new data as it becomes available),
		- medium_term (approximately last 6 months),
		- short_term (approximately last 4 weeks).
		:return: List[:class:`SimpleTrack`]
		'''

		if limit > 50:
			raise SpoofyException('Limit must be less or equal to 50.')

		data = await self.http.get_me_top_tracks(limit=limit, offset=offset, time_range=time_range)

		tracks = []
		for track_obj in data['items']:
			tracks.append(SimpleTrack(self, track_obj))

		return tracks

	async def get_me_top_artists(self, limit=20, offset=0, time_range='medium_term'):
		'''
		Get the top artists of the current user.

		:param int limit: How many artists to return. Maximum is 50.
		:param int offset: The index of the first result to return.
		:param str time_range: The time period for which data are selected to form a top. Valid values:
		- long_term (calculated from several years of data and including all new data as it becomes available),
		- medium_term (approximately last 6 months),
		- short_term (approximately last 4 weeks).
		:return: List[:class:`SimpleArtist`]
		'''

		if limit > 50:
			raise SpoofyException('Limit must be less or equal to 50.')

		data = await self.http.get_me_top_artists(limit=limit, offset=offset, time_range=time_range)

		artists = []
		for artist_obj in data['items']:
			artists.append(SimpleArtist(self, artist_obj))

		return artists

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

	async def create_playlist(self, user, name='Unnamed playlist', description=None, public=False, collaborative=False):
		'''
		Create a new playlist.

		:param user: :class:`User` instance or Spotify ID.
		:param str name: Name of the new playlist.
		:param str description: Description of the new playlist.
		:param bool public: Whether the playlist should be public.
		:param bool collaborative: Whether the playlist should be collaborative (anyone can edit it).
		:return: A :class:`FullPlaylist` instance.
		'''

		data = await self.http.create_playlist(user, name, description, public, collaborative)

		playlist = FullPlaylist(self, data)
		playlist._tracks = {}

		return playlist

	async def edit_playlist(self, playlist, name=None, description=None, public=None, collaborative=None):
		'''
		Edit a playlist.

		:param playlist: :class:`Playlist` instance or Spotify ID.
		:param str name: New name of the playlist.
		:param str description: New description of the playlist.
		:param bool public: New public state of the playlist.
		:param bool collaborative: New collaborative state of the playlist.
		'''

		playlist = self._get_id(playlist)

		await self.http.edit_playlist(
			playlist_id=playlist,
			name=name,
			description=description,
			public=public,
			collaborative=collaborative
		)

	async def playlist_add_tracks(self, playlist, tracks, position=0):
		'''
		Add several tracks to a playlist.

		:param playlist: :class:`Playlist` instance or Spotify ID.
		:param tracks: List of Spotify IDs or :class:`Track` instance (or a mix).
		:param int position: Position in the playlist to insert tracks.
		'''

		playlist = self._get_id(playlist)

		tracks_fin = []

		for index, track in enumerate(tracks):
			if isinstance(track, Object):
				track = track.id
			if not track.startswith('spotify:track:'):
				track = 'spotify:track:' + track
			tracks_fin.append(track)

		for slice in SliceIterator(tracks_fin, 100):
			await self.http.playlist_add_tracks(playlist, slice, position=position)

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

	async def get_playlist_tracks(self, playlist):
		'''
		Get tracks from a playlist.

		:param playlist: :class:`Playlist` instance or Spotify ID.
		:return: List[:class:`PlaylistTrack`]
		'''

		playlist = self._get_id(playlist)

		data = await self.http.get_playlist_tracks(playlist)

		tracks = []

		async for track in Pager(self.http, data):
			tracks.append(PlaylistTrack(self, track))

		return tracks

	async def get_user_playlists(self, user):
		'''
		Get a list of attainable playlists a user owns.

		:param user: :class:`User` instance or Spotify ID.
		:return: List[:class:`SimplePlaylist`]
		'''

		user = self._get_id(user)

		data = await self.http.get_user_playlists(user)

		playlists = []

		async for playlist_obj in Pager(self.http, data):
			if playlist_obj is None:
				playlists.append(None)
			else:
				playlist = SimplePlaylist(self, playlist_obj)
				await playlist._fill_tracks(
					PlaylistTrack,
					Pager(self.http, await self.http.get_playlist_tracks(playlist.id))
				)
				playlists.append(playlist)

		return playlists

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

	async def get_tracks(self, *track_ids):
		'''
		Get several tracks.

		:param str track_ids: List of track Spotify IDs.
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

	async def get_audio_features(self, track):
		'''
		Get 'Audio Features' of a track.

		:param track: :class:`Track` instance or Spotify ID.
		:return: :class:`AudioFeatures`
		'''

		track = self._get_id(track)

		try:
			data = await self.http.get_audio_features(track)
		except NotFound:
			return None

		return AudioFeatures(self, data)

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

	async def get_artist_albums(self, artist_id, limit=50, **kwargs):
		'''
		Get an artist's albums
		:param str artist_id: Spotify ID of artist.
		:param int limit: How many albums to return.
		:param kwargs: other query params for this method
		:return: List[:class:`SimpleAlbum`]
		'''
		try:
			data = await self.http.get_artist_albums(artist_id, limit=limit if limit < 50 else 50, **kwargs)
		except NotFound:
			return None

		albums = []

		async for album_obj in Pager(self.http, data, limit):
			albums.append(SimpleAlbum(self, album_obj))

		return albums

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

	async def get_artist_top_tracks(self, artist, market='from_token'):
		'''
		Returns the top tracks for an artist.

		:param artist: :class:`Artist` instance or Spotify ID.
		:param market: Market to find tracks for.
		:return: A list of maximum 10 :class:`FullTrack` instances.
		'''

		artist_id = self._get_id(artist)

		data = await self.http.get_artist_top_tracks(artist_id, market=market)

		tracks = []
		for track_obj in data['tracks']:
			tracks.append(FullTrack(self, track_obj))

		return tracks

	async def get_artist_related_artists(self, artist):
		'''
		Get an artists related artists.

		:param artist: :class:`Artist` or Spotify ID.
		:return: A list of maximum 20 :class:`FullArtist` instances.
		'''

		artist_id = self._get_id(artist)

		data = await self.http.get_artist_related_artists(artist_id)

		artists = []
		for artist_obj in data['artists']:
			artists.append(FullArtist(self, artist_obj))

		return artists

	async def get_album(self, album_id, **kwargs):
		'''
		Get an album.

		:param str album_id: Spotify ID of album.
		:param kwargs: other query params for this method
		:return: :class:`FullAlbum` instance.
		'''

		try:
			data = await self.http.get_album(album_id, **kwargs)
		except NotFound:
			return None

		album = FullAlbum(self, data)
		await album._fill_tracks(SimpleTrack, Pager(self.http, data['tracks']))

		return album

	async def get_albums(self, *album_ids, **kwargs):
		'''
		Get several albums.

		:param str album_ids: Spotify ID of album.
		:param kwargs: other query params for this method
		:return: List[:class:`FullAlbum`]
		'''

		chunks = [album_ids[x:x + 20] for x in range(0, len(album_ids), 20)]
		albums = []

		for chunk in chunks:
			data = await self.http.get_albums(chunk, **kwargs)

			for album_obj in data['albums']:
				if album_obj is None:
					albums.append(None)
				else:
					album = FullAlbum(self, album_obj)
					await album._fill_tracks(SimpleTrack, Pager(self.http, album_obj['tracks']))
					albums.append(album)

		return albums

	async def get_album_tracks(self, album, **kwargs):
		'''
		Get tracks from an album.

		:param album: :class:`Album` or Spotify ID of album.
		:param kwargs: other query params for this method
		:return: List[:class:`SimpleTrack`]
		'''

		album = self._get_id(album)

		data = await self.http.get_album_tracks(album, **kwargs)

		tracks = []

		async for track_obj in Pager(self.http, data):
			tracks.append(SimpleTrack(self, track_obj))

		return tracks

	async def get_followed_artists(self, type='artist', limit=float('inf')):
		'''
		Get user's followed artists

		:param str type: The ID type: currently only artist is supported.
		:param int limit: The maximum number of items to return. Default - infinity
		:return: list[:class:`SimpleArtist`]
		'''
		data = await self.http.get_followed_artists(type=type, limit=limit if limit < 50 else 50)

		artists = []

		if type == 'artist':
			async for artist_obj in CursorBasedPaging(self.http, data, 'artists', limit):
				artists.append(SimpleArtist(self, artist_obj))
		else:
			raise SpoofyException('Currently only artist is supported.')

		return artists

	async def following(self, type, *ids, **kwargs):
		'''
		Follow artists or users

		:param str type: The ID type: either artist or user.
		:param str ids: Spotify ID of the artist or the user.
		:param kwargs: other query params for this method
		'''

		chunks = [ids[x:x + 50] for x in range(0, len(ids), 50)]

		for chunk in chunks:
			await self.http.following(type=type, ids=chunk, **kwargs)

	async def close_session(self):
		await self.http.close_session()
