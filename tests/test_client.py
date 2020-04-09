import string
from collections import namedtuple
from datetime import timedelta
from random import choices

from pytest import fixture, mark, raises

from asyncspotify import *
from config import *

from pytest import fixture, mark, raises

User = namedtuple('User', 'id name')
Playlist = namedtuple('Playlist', 'id ownerid')

pytestmark = mark.asyncio


@fixture(scope='class')
async def sp():
	async with Client(ClientCredentialsFlow(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)) as sp:
		yield sp


@fixture()
def good_track_id():
	return '1mea3bSkSGXuIRvnydlB5b'


@fixture()
def good_album_id():
	return '79dL7FLiJFOO0EoehUHQBv'


@fixture()
def good_artist_id():
	return '5INjqkS1o8h1imAzPqGZBb'


@fixture()
def good_playlist():
	return Playlist('6WCb77q7WBfYbKT9VYst3R', 'runie13')


@fixture()
def bad_id():
	return 'ææææææææææææææææææææææ'


@fixture()
def user():
	return User('runie13', 'runie13')


@fixture()
def query():
	return 'tennyson'


@fixture()
def bad_query():
	return ''.join(choices(string.ascii_letters + string.digits, k=128))


class TestClient:
	async def test_search(self, sp: Client, query, bad_query):
		# no type specification
		with raises(BadRequest):
			await sp.search(q=query)

		# unknown type
		with raises(BadRequest):
			await sp.search('not_a_type', q=query)

		# same but variadic
		with raises(BadRequest):
			await sp.search('track', 'asd', q=query)

		res = await sp.search('track', 'album', q=query)
		assert len(res) == 2
		assert 'tracks' in res
		assert 'albums' in res
		assert len(res['tracks']) == 20
		assert len(res['albums']) == 20

		res = await sp.search_tracks(q=query, limit=3)
		assert len(res) == 3
		assert all(isinstance(track, SimpleTrack) for track in res)

		res = await sp.search_artists(q=query, limit=3)
		assert len(res) == 3
		assert all(isinstance(artist, FullArtist) for artist in res)

		res = await sp.search_albums(q=query, limit=3)
		assert len(res) == 3
		assert all(isinstance(album, SimpleAlbum) for album in res)

		res = await sp.search_playlists(q=query, limit=3)
		assert len(res) == 3
		assert all(isinstance(playlist, SimplePlaylist) for playlist in res)

		assert isinstance(await sp.search_track(q=query), SimpleTrack)
		assert isinstance(await sp.search_artist(q=query), FullArtist)
		assert isinstance(await sp.search_album(q=query), SimpleAlbum)
		assert isinstance(await sp.search_playlist(q=query), SimplePlaylist)

		assert await sp.search_playlist(q=bad_query) is None
		assert await sp.search_track(q=bad_query) is None
		assert await sp.search_artist(q=bad_query) is None
		assert await sp.search_album(q=bad_query) is None

	async def test_track(self, sp: Client, good_track_id, bad_id):
		track = await sp.get_track(good_track_id)

		assert track.id == good_track_id

		assert isinstance(track.album, SimpleAlbum)
		assert isinstance(track.popularity, int)

		# mixins
		assert isinstance(track.external_ids, dict)
		assert isinstance(track.external_urls, dict)
		for artist in track.artists:
			assert isinstance(artist, SimpleArtist)

		# bad IDs should just return None
		with raises(BadRequest):
			await sp.get_track(bad_id)

		with raises(BadRequest):
			await sp.get_tracks(good_track_id, bad_id)

	async def test_album(self, sp: Client, good_album_id, bad_id):
		album = await sp.get_album(good_album_id)

		assert album.id == good_album_id

		assert isinstance(album.popularity, int)

		# mixins
		assert isinstance(album.external_ids, dict)
		assert isinstance(album.external_urls, dict)

		for track in album.tracks:
			assert isinstance(track, SimpleTrack)

		for image in album.images:
			assert isinstance(image, Image)
			assert hasattr(image, 'width')
			assert hasattr(image, 'height')

		for artist in album.artists:
			assert isinstance(artist, SimpleArtist)

		# bad IDs should just return None
		with raises(BadRequest):
			await sp.get_album(bad_id)

		with raises(BadRequest):
			await sp.get_tracks(good_album_id, bad_id)

	async def test_artist(self, sp: Client, good_artist_id, bad_id):
		artist = await sp.get_artist(good_artist_id)

		assert artist.id == good_artist_id
		assert isinstance(artist.popularity, int)

		# mixins
		assert isinstance(artist.external_urls, dict)

		for image in artist.images:
			assert isinstance(image, Image)

		# bad IDs should just return None
		with raises(BadRequest):
			await sp.get_artist(bad_id)

		with raises(BadRequest):
			await sp.get_artists(good_artist_id, bad_id)

	async def test_playlist(self, sp: Client, good_playlist, bad_id):
		good_playlist_id = good_playlist.id
		good_playlist_owner_id = good_playlist.ownerid

		playlist = await sp.get_playlist(good_playlist_id)

		assert playlist.id == good_playlist_id
		assert isinstance(playlist.owner, PublicUser)
		assert playlist.owner.id == good_playlist_owner_id
		assert isinstance(playlist.follower_count, int)

		# mixins
		assert isinstance(playlist.external_urls, dict)

		for track in playlist.tracks:
			assert isinstance(track, PlaylistTrack)

		for image in playlist.images:
			assert isinstance(image, Image)

		with raises(BadRequest):
			await sp.get_playlist(bad_id)

	async def test_get_playlist_tracks(self, sp: Client, good_playlist):
		good_playlist_id = good_playlist.id

		tracks = await sp.get_playlist_tracks(good_playlist_id)

		assert isinstance(tracks, list)

		for track in tracks:
			assert isinstance(track, PlaylistTrack)

	async def test_get_user(self, sp: Client, user):
		fetched = await sp.get_user(user.id)
		assert fetched.id == user.id
		assert fetched.name == user.name

	async def test_audio_features(self, sp: Client, good_track_id, bad_id):
		audio_features = await sp.get_audio_features(good_track_id)

		assert audio_features.id == good_track_id
		assert isinstance(audio_features.acousticness, float)
		assert isinstance(audio_features.track_href, str)
		assert isinstance(audio_features.duration, timedelta)

		with raises(BadRequest):
			await sp.get_audio_features(bad_id)

	async def test_get_audio_features_multiple_tracks(self, sp: Client, good_track_id, bad_id):
		audio_features = await sp.get_audio_features_multiple_tracks(good_track_id)
		audio_features = audio_features[0]

		assert audio_features.id == good_track_id
		assert isinstance(audio_features.acousticness, float)
		assert isinstance(audio_features.track_href, str)
		assert isinstance(audio_features.duration, timedelta)

		with raises(BadRequest):
			await sp.get_audio_features(bad_id)

	async def test_get_artist_top_tracks(self, sp: Client, good_artist_id):
		tracks = await sp.get_artist_top_tracks(good_artist_id)

		assert len(tracks)

		for track in tracks:
			assert isinstance(track, FullTrack)

	async def test_get_artist_related_artists(self, sp: Client, good_artist_id):
		artists = await sp.get_artist_related_artists(good_artist_id)

		assert len(artists)

		for artist in artists:
			assert isinstance(artist, FullArtist)

	async def test_get_artist_albums(self, sp: Client, good_artist_id):
		albums = await sp.get_artist_albums(good_artist_id, limit=3)

		assert len(albums) == 3

		for album in albums:
			assert isinstance(album, SimpleAlbum)
			assert not hasattr(album, 'tracks')

		with raises(BadRequest):
			await sp.get_artist_albums(bad_id)
