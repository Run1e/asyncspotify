import logging
from datetime import timedelta
from typing import List

from .album import FullAlbum, SimpleAlbum
from .artist import FullArtist, SimpleArtist
from .audiofeatures import AudioFeatures
from .device import Device
from .exceptions import *
from .http import HTTP
from .oauth.flows import Authenticator, RefreshableMixin
from .object import SpotifyObject
from .pager import CursorBasedPaging, Pager, SearchPager
from .playing import CurrentlyPlaying, CurrentlyPlayingContext
from .playlist import FullPlaylist, SimplePlaylist
from .track import FullTrack, PlaylistTrack, SimpleTrack
from .user import PrivateUser, PublicUser
from .utils import subslice

log = logging.getLogger(__name__)


def get_id(obj):
	if isinstance(obj, SpotifyObject):
		return obj.id
	else:
		return obj


class Client:
	'''
	Client interface for the API.

	This is the class you should be interfacing with when fetching Spotify objects.

	auth: :class:`Authenticator`
		Authenticator instance used for authenticating with the API.
	'''

	auth: Authenticator
	http: HTTP

	def __init__(self, auth):
		'''
		Creates a Spotify Client instance.

		:param auth: Instance of :class:`Authenticator`
		'''

		self.auth = auth(self)
		self.http = HTTP(self)

	async def __aenter__(self):
		await self.auth.authorize()
		return self

	async def __aexit__(self, exc_type, exc_val, exc_tb):
		await self.close()

	async def authorize(self):
		'''Tell the authenticator to authorize this client.'''
		await self.auth.authorize()

	async def refresh(self):
		'''Tell the authenticator to refresh this client, if applicable.'''
		await self.auth.refresh()

	async def close(self):
		'''Close this client session.'''

		if isinstance(self.auth, RefreshableMixin):
			self.auth._task.cancel()

		await self.http.close_session()

	def _ensure_market(self, market):
		return self.auth.market if market is None else market

	async def get_player(self, **kwargs) -> CurrentlyPlayingContext:
		'''
		Get a context for what user is currently playing.

		:param kwargs: query params for this request
		:return: :class:`PlayingContext`
		'''

		data = await self.http.get_player(**kwargs)

		return CurrentlyPlayingContext(self, data)

	async def player_currently_playing(self, **kwargs) -> CurrentlyPlaying:
		data = await self.http.player_currently_playing(**kwargs)

		return CurrentlyPlaying(self, data)

	async def get_devices(self) -> List[Device]:
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

		await self.http.player_next(device_id=get_id(device))

	async def player_prev(self, device=None):
		'''
		Play the previous track.

		:param device: :class:`Device` or Spotify ID.
		'''

		await self.http.player_prev(device_id=get_id(device))

	async def player_play(self, device=None, **kwargs):
		'''
		Start playback on device.

		:param device: :class:`Device` or Spotify ID.
		:param kwargs: body params of the request.

		Example:

		.. code-block:: py

			player_play(
				context_uri='spotify:album:6xKK037rfCf2f6gf30SpvL',
				offset=dict(uri='spotify:track:2beor6qrB0XJxW1CM6X9x2'),
				position_ms=98500
			)
		'''

		await self.http.player_play(device_id=get_id(device), **kwargs)

	async def player_pause(self, device=None):
		'''
		Stop playback on a device.

		:param device: :class:`Device` or Spotify ID.
		'''

		await self.http.player_pause(device_id=get_id(device))

	async def player_seek(self, time, device=None):
		'''
		Seek to a point in the currently playing track.

		:param time: timedelta object or milliseconds (integer)
		:param device: :class:`Device` or Spotify ID.
		'''

		if isinstance(time, timedelta):
			time = time.days * (1000 * 60 * 60 * 24) + time.seconds * 1000 + time.microseconds // 1000
		await self.http.player_seek(time, get_id(device))

	async def player_repeat(self, state, device=None):
		'''
		Set player repeat mode.

		:param str state: Can be 'track', 'context' or 'off'.
		:param device: :class:`Device` or Spotify ID.
		'''

		await self.http.player_repeat(state, get_id(device))

	async def player_volume(self, volume, device=None):
		'''
		Set player volume.

		:param int volume: Value from 0 to 100.
		:param device: :class:`Device` or Spotify ID.
		'''

		await self.http.player_volume(volume, get_id(device))

	async def player_shuffle(self, state, device=None):
		'''
		Set player shuffle mode.

		:param bool state: Shuffle mode state.
		:param device: :class:`Device` or Spotify ID.
		'''

		await self.http.player_shuffle(state, get_id(device))

	async def search(self, *types, q, market=None, limit=None, offset=None, include_external=None) -> dict:
		'''
		Searches for tracks, artists, albums and/or playlists.

		:param types: One or more of the strings ``track``, ``album``, ``artist``, ``playlist`` or the class equivalents.
		:param str q: The search query. See Spotifys' query construction guide `here. <https://developer.spotify.com/documentation/web-api/reference/search/search/>`_
		:param market: ISO-3166-1_ country code or the string ``from_token``.
		:param int limit: How many results of each type to return.
		:param offset: Where to start the pagination.
		:param include_external: If this is equal to ``audio``, the specified the response will include any relevant audio content that is hosted externally.

		:return: A dict with a key for each type, whose values are a list of instances.
		'''

		actual_types = []
		for type in types:
			if isinstance(type, (SimpleTrack, SimpleAlbum, SimpleArtist, SimplePlaylist)):
				actual_types.append(type._type)
			elif isinstance(type, str):
				actual_types.append(type.lower())
			else:
				raise ValueError('Unknown type: %s' % str(type))

		data = await self.http.search(
			q, ','.join(actual_types),
			market=market,
			limit=limit,
			offset=offset,
			include_external=include_external
		)

		results = {}

		if 'tracks' in data:
			results['tracks'] = []
			async for track_obj in SearchPager(self.http, data, 'tracks', limit):
				results['tracks'].append(SimpleTrack(self, track_obj))

		if 'albums' in data:
			results['albums'] = []
			async for album_obj in SearchPager(self.http, data, 'albums', limit):
				results['albums'].append(SimpleAlbum(self, album_obj))

		if 'artists' in data:
			results['artists'] = []
			async for artist_obj in SearchPager(self.http, data, 'artists', limit):
				results['artists'].append(FullArtist(self, artist_obj))

		if 'playlists' in data:
			results['playlists'] = []
			async for artist_obj in SearchPager(self.http, data, 'playlists', limit):
				results['playlists'].append(SimplePlaylist(self, artist_obj))

		return results

	async def search_tracks(self, q, market=None, limit=None, offset=None, include_external=None) -> List[SimpleTrack]:
		'''
		Alias for ``Client.search('track', ...)``

		:return: List[:class:`SimpleTrack`]
		'''

		results = await self.search(
			'track', q=q, market=market, limit=limit, offset=offset, include_external=include_external
		)
		return results['tracks']

	async def search_artists(self, q, market=None, limit=None, offset=None, include_external=None) -> List[FullArtist]:
		'''
		Alias for ``Client.search('artist, ...)``

		:return: List[:class:`FullArtist`]
		'''

		results = await self.search(
			'artist', q=q, market=market, limit=limit, offset=offset, include_external=include_external
		)
		return results['artists']

	async def search_albums(self, q, market=None, limit=None, offset=None, include_external=None) -> List[SimpleAlbum]:
		'''
		Alias for ``Client.search('album', ...)``

		:return: List[:class:`SimpleAlbum`]
		'''

		results = await self.search(
			'album', q=q, market=market, limit=limit, offset=offset, include_external=include_external
		)
		return results['albums']

	async def search_playlists(self, q, market=None, limit=None, offset=None, include_external=None) -> List[
		SimplePlaylist]:
		'''
		Alias for ``Client.search('playlist', ...)``

		:return: List[:class:`SimplePlaylist`]
		'''

		results = await self.search(
			'playlist', q=q, market=market, limit=limit, offset=offset, include_external=include_external
		)
		return results['playlists']

	async def search_track(self, q=None) -> SimpleTrack:
		'''
		Returns the top track for the query.

		:return: :class:`SimpleTrack` or None
		'''

		results = await self.search_tracks(q=q, limit=1)
		return results[0] if results else None

	async def search_artist(self, q=None) -> FullArtist:
		'''
		Returns the top artist for the query.

		:return: :class:`SimpleArtist` or None
		'''

		results = await self.search_artists(q=q, limit=1)
		return results[0] if results else None

	async def search_album(self, q=None) -> SimpleAlbum:
		'''
		Returns the top album for the query.

		:return: :class:`SimpleAlbum`
		'''

		results = await self.search_albums(q=q, limit=1)
		return results[0] if results else None

	async def search_playlist(self, q=None) -> SimplePlaylist:
		'''
		Returns the top playlist for the query.

		:return: :class:`SimplePlaylist`
		'''

		results = await self.search_playlists(q=q, limit=1)
		return results[0] if results else None

	async def get_me(self) -> PrivateUser:
		'''
		Gets the current user.

		:return: A :class:`PrivateUser` instance of the current user.
		'''

		data = await self.http.get_me()
		return PrivateUser(self, data)

	async def get_me_top_tracks(self, limit=None, offset=None, time_range=None) -> List[SimpleTrack]:
		'''
		Gets the top tracks of the current user.

		Requires scope ``user-top-read``.

		:param int limit: How many tracks to return. Maximum is 50.
		:param int offset: The index of the first result to return.
		:param str time_range: The time period for which data are selected to form a top.

		Valid values for ``time_range``
		  - ``long_term`` (calculated from several years of data and including all new data as it becomes available),
		  - ``medium_term`` (approximately last 6 months),
		  - ``short_term`` (approximately last 4 weeks).

		:return: List[:class:`SimpleTrack`]
		'''

		if limit > 50:
			raise SpotifyException('Limit must be less or equal to 50.')

		data = await self.http.get_me_top_tracks(limit=limit, offset=offset, time_range=time_range)

		tracks = []
		for track_obj in data['items']:
			tracks.append(SimpleTrack(self, track_obj))

		return tracks

	async def get_me_top_artists(self, limit=20, offset=0, time_range='medium_term') -> List[SimpleArtist]:
		'''
		Get the top artists of the current user.

		:param int limit: How many artists to return. Maximum is 50.
		:param int offset: The index of the first result to return.
		:param str time_range: The time period for which data are selected to form a top.

		Valid values for ``time_range``
		  - ``long_term`` (calculated from several years of data and including all new data as it becomes available),
		  - ``medium_term`` (approximately last 6 months),
		  - ``short_term`` (approximately last 4 weeks).

		:return: List[:class:`SimpleArtist`]
		'''

		if limit > 50:
			raise SpotifyException('Limit must be less or equal to 50.')

		data = await self.http.get_me_top_artists(limit=limit, offset=offset, time_range=time_range)

		artists = []
		for artist_obj in data['items']:
			artists.append(SimpleArtist(self, artist_obj))

		return artists

	async def get_user(self, user_id) -> PublicUser:
		'''
		Get a user.

		:param str user_id: Spotify ID of user.
		:return: A :class:`PublicUser` instance.
		'''

		data = await self.http.get_user(user_id)

		return PublicUser(self, data)

	async def create_playlist(self, user, name, public=False, collaborative=False, description=None) -> FullPlaylist:
		'''
		Create a new playlist.

		:param user: :class:`User` instance or Spotify ID.
		:param str name: Name of the new playlist.
		:param str description: Description of the new playlist.
		:param bool public: Whether the playlist should be public.
		:param bool collaborative: Whether the playlist should be collaborative (anyone can edit it).
		:return: A :class:`FullPlaylist` instance.
		'''

		data = await self.http.create_playlist(
			get_id(user), name,
			public=public,
			collaborative=collaborative,
			description=description
		)

		playlist = FullPlaylist(self, data)
		playlist._tracks = dict()

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

		await self.http.edit_playlist(
			playlist_id=get_id(playlist),
			name=name,
			description=description,
			public=public,
			collaborative=collaborative
		)

	async def playlist_add_tracks(self, playlist, *tracks, position=None):
		'''
		Add several tracks to a playlist.

		:param playlist: :class:`Playlist` instance or Spotify ID.
		:param tracks: List of Spotify IDs or :class:`Track` instance (or a mix).
		:param int position: Position in the playlist to insert tracks.
		'''

		playlist = get_id(playlist)

		uris = []

		for track in tracks:
			track = get_id(track)

			if not track.startswith('spotify:track:'):
				track = 'spotify:track:' + track

			uris.append(track)

		for chunk in subslice(uris, 100):
			await self.http.playlist_add_tracks(playlist, uris=chunk, position=position)

	async def get_playlist(self, playlist_id) -> FullPlaylist:
		'''
		Get a pre-existing playlist.

		:param str playlist_id: Spotify ID of the playlist.
		:return: :class:`FullPlaylist` instance.
		'''

		data = await self.http.get_playlist(playlist_id)

		playlist = FullPlaylist(self, data)
		await playlist._fill_tracks(PlaylistTrack, Pager(self.http, data.pop('tracks')))

		return playlist

	async def get_playlist_tracks(self, playlist) -> List[PlaylistTrack]:
		'''
		Get tracks from a playlist.

		:param playlist: :class:`Playlist` instance or Spotify ID.
		:return: List[:class:`PlaylistTrack`]
		'''

		playlist = get_id(playlist)

		data = await self.http.get_playlist_tracks(playlist)

		tracks = []

		async for track in Pager(self.http, data):
			tracks.append(PlaylistTrack(self, track))

		return tracks

	async def get_user_playlists(self, user) -> List[SimplePlaylist]:
		'''
		Get a list of attainable playlists a user owns.

		:param user: :class:`User` instance or Spotify ID.
		:return: List[:class:`SimplePlaylist`]
		'''

		user = get_id(user)

		data = await self.http.get_user_playlists(user)

		playlists = []

		async for playlist_obj in Pager(self.http, data):
			if playlist_obj is None:
				playlists.append(None)
			else:
				playlist = SimplePlaylist(self, playlist_obj)
				pager = Pager(self.http, await self.http.get_playlist_tracks(playlist.id))
				await playlist._fill_tracks(PlaylistTrack, pager)
				playlists.append(playlist)

		return playlists

	async def get_track(self, track_id) -> FullTrack:
		'''
		Get a track.

		:param str track_id: Spotify ID of track.
		:return: :class:`FullTrack` instance.
		'''

		data = await self.http.get_track(track_id)
		return FullTrack(self, data)

	async def get_tracks(self, *track_ids) -> List[FullTrack]:
		'''
		Get several tracks.

		:param str track_ids: List of track Spotify IDs.
		:return: List[:class:`FullTrack`]
		'''

		tracks = []

		for chunk in subslice(track_ids, 50):
			data = await self.http.get_tracks(','.join(get_id(obj) for obj in chunk))

			for track_obj in data['tracks']:
				if track_obj is None:
					tracks.append(None)
				else:
					tracks.append(FullTrack(self, track_obj))

		return tracks

	async def get_audio_features(self, track) -> AudioFeatures:
		'''
		Get 'Audio Features' of a track.

		:param track: :class:`Track` instance or Spotify ID.
		:return: :class:`AudioFeatures`
		'''

		track = get_id(track)

		data = await self.http.get_audio_features(track)

		return AudioFeatures(self, data)

	async def get_artist(self, artist_id) -> FullArtist:
		'''
		Get an artist.

		:param str artist_id: Spotify ID of artist.
		:return: :class:`FullArtist` instance.
		'''

		data = await self.http.get_artist(artist_id)

		return FullArtist(self, data)

	async def get_artist_albums(self, artist_id, include_groups=None, country=None, limit=None, offset=None) -> List[SimpleAlbum]:
		'''
		Get an artist's albums.

		.. note::
		   This endpoint does *not* return the track objects for each album. If you need those, you have to
		   fetch them manually afterwards.

		:param str artist_id: Spotify ID of artist.
		:param int limit: How many albums to return.
		:param kwargs: other query params for this method
		:return: List[:class:`SimpleAlbum`]
		'''

		albums = []

		data = await self.http.get_artist_albums(
			artist_id, include_groups=include_groups, country=country, limit=limit, offset=offset
		)

		async for album_obj in Pager(self.http, data):
			albums.append(SimpleAlbum(self, album_obj))

		return albums

	async def get_artists(self, *artist_ids) -> List[FullArtist]:
		'''
		Get several artists.

		:param artist_ids: List of artist Spotify IDs.
		:return: List[:class:`FullArtist`]
		'''

		artists = []

		for chunk in subslice(artist_ids, 2):
			data = await self.http.get_artists(','.join(get_id(obj) for obj in chunk))

			for artist_obj in data['artists']:
				if artist_obj is None:
					artists.append(None)
				else:
					artists.append(FullArtist(self, artist_obj))

		return artists

	async def get_artist_top_tracks(self, artist, market=None) -> List[FullTrack]:
		'''
		Returns the top tracks for an artist.

		:param artist: :class:`Artist` instance or Spotify ID.
		:param market: ISO-3166_1_ country code. Leave blank to let the library auto-resolve this.
		:return: A list of maximum 10 :class:`FullTrack` instances.
		'''

		artist_id = get_id(artist)
		market = self._ensure_market(market)

		data = await self.http.get_artist_top_tracks(artist_id, market=market)

		tracks = []

		for track_obj in data['tracks']:
			tracks.append(FullTrack(self, track_obj))

		return tracks

	async def get_artist_related_artists(self, artist) -> List[FullArtist]:
		'''
		Get an artists related artists.

		:param artist: :class:`Artist` or Spotify ID.
		:return: A list of maximum 20 :class:`FullArtist` instances.
		'''

		artist_id = get_id(artist)

		data = await self.http.get_artist_related_artists(artist_id)

		artists = []

		for artist_obj in data['artists']:
			artists.append(FullArtist(self, artist_obj))

		return artists

	async def get_album(self, album_id, market=None) -> FullAlbum:
		'''
		Get an album.

		:param str album_id: Spotify ID of album.
		:param market: ISO-3166-1_ country code.
		:return: :class:`FullAlbum` instance.
		'''

		data = await self.http.get_album(album_id, market=market)

		album = FullAlbum(self, data)
		await album._fill_tracks(SimpleTrack, Pager(self.http, data['tracks']))

		return album

	async def get_albums(self, *album_ids, market=None) -> List[FullAlbum]:
		'''
		Get several albums.

		:param str album_ids: Spotify ID of album.
		:param market: ISO-3166-1_ country code.
		:return: List[:class:`FullAlbum`]
		'''

		albums = []

		for chunk in subslice(album_ids, 20):
			data = await self.http.get_albums(','.join(get_id(obj) for obj in chunk), market=market)

			for album_obj in data['albums']:
				if album_obj is None:
					albums.append(None)
				else:
					album = FullAlbum(self, album_obj)
					await album._fill_tracks(SimpleTrack, Pager(self.http, album_obj['tracks']))
					albums.append(album)

		return albums

	async def get_album_tracks(self, album, limit=None, offset=None, market=None) -> List[SimpleTrack]:
		'''
		Get tracks from an album.

		:param album: :class:`Album` or Spotify ID of album.
		:param limit: How many tracks to fetch.
		:param offset: What pagination offset to start from.
		:param market: ISO-3166-1_ country code.
		:return: List[:class:`SimpleTrack`]
		'''

		album = get_id(album)

		data = await self.http.get_album_tracks(album, limit=limit, offset=offset, market=market)

		tracks = []

		async for track_obj in Pager(self.http, data):
			tracks.append(SimpleTrack(self, track_obj))

		return tracks

	async def get_followed_artists(self, type='artist', limit=None, after=None) -> List[SimpleArtist]:
		'''
		Get user's followed artists

		:param str type: The ID type: currently only artist is supported.
		:param int limit: The maximum number of items to return. Default - infinity
		:param after: What artist ID to start the fetching from.
		:return: List[:class:`SimpleArtist`]
		'''

		if type != 'artist':
			raise SpotifyException('Currently only artist is supported.')

		data = await self.http.get_followed_artists(type=type, limit=limit, after=after)

		artists = []

		async for artist_obj in CursorBasedPaging(self.http, data, 'artists', limit):
			artists.append(SimpleArtist(self, artist_obj))

		return artists

	async def following(self, type, *ids, limit=None, after=None):
		'''
		Follow artists or users.

		:param str type: The ID type: either artist or user.
		:param str ids: Spotify ID of the artist or the user.
		:param limit: Maximum number of items to return.
		:param after: The last artist ID retrieved from the previous request.
		'''

		for chunk in subslice(ids, 50):
			await self.http.following(type=type, ids=','.join(get_id(obj) for obj in chunk), limit=limit, after=after)
