import asyncio
import logging
from asyncio import Lock, sleep
from json import JSONDecodeError, loads
from urllib.parse import urlencode

from aiohttp import ClientSession

from .exceptions import *

log = logging.getLogger(__name__)


def filter_nones(kwargs):
	return {k: v for k, v in kwargs.items() if v is not None}


class Route:
	BASE = 'https://api.spotify.com/v1'

	def __init__(self, method: str, url: str, **params):
		self.method = method.upper()
		self.url = url if url.startswith('http') else '{0}/{1}'.format(self.BASE, url)
		self.params = {k: v for k, v in params.items() if v is not None}

	def __repr__(self):
		return '<Route {0.method} url={0.url} params={0.params}>'.format(self)

	def __str__(self):
		ret = self.url
		if self.params:
			ret += '?' + urlencode(self.params)
		return ret


class HTTP:
	_attempts = 5

	def __init__(self, client, loop=None):
		self.client = client
		self.session = ClientSession(loop=loop or asyncio.get_event_loop())
		self.lock = Lock()

	async def close_session(self):
		await self.session.close()

	async def request(self, route, data=None, json=None, headers=None, authorize=True):

		if authorize:
			auth_header = self.client.auth.header
			if auth_header is None:
				raise AuthenticationError('Authorize before attempting an authorized request.')

			if headers:
				headers.update(auth_header)
			else:
				headers = auth_header

		kw = dict(method=route.method, url=route.url, headers=headers)

		if route.params:
			kw['params'] = route.params

		if data:
			kw['data'] = data

		if json:
			kw['json'] = json
			kw['headers']['Content-Type'] = 'application/json'

		async with self.lock:
			for attempt in range(self._attempts):

				async with self.session.request(**kw) as r:
					status_code = r.status
					headers = r.headers
					text = await r.text()

					log.debug('[%s] %s', status_code, repr(route))

					try:
						data = loads(text)
					except JSONDecodeError:
						data = None

					if 200 <= status_code < 300:
						return data

					try:
						error = data['error']['message']
					except (TypeError, KeyError):
						error = None

					if status_code == 429:
						retry_after = int(headers.get('Retry-After', 1)) + 1
						log.warning('Rate limited. Retrying in %s seconds.', retry_after)
						await sleep(retry_after)
						continue

					elif status_code == 400:
						raise BadRequest(r, error)

					elif status_code == 401:
						raise Unauthorized(r, error)

					elif status_code == 403:
						raise Forbidden(r, error)

					elif status_code == 404:
						raise NotFound(r, error)

					elif status_code == 405:
						raise NotAllowed(r, error)

					elif status_code >= 500:
						continue

					else:
						raise HTTPException(r, 'Unhandled HTTP status code: %s' % status_code)

		raise HTTPException(r, 'Request failed 5 times.')

	async def get_player(self, **kwargs):
		r = Route('GET', 'me/player', **kwargs)
		return await self.request(r)

	async def player_currently_playing(self, **kwargs):
		r = Route('GET', 'me/player/currently-playing', **kwargs)
		return await self.request(r)

	async def get_devices(self):
		r = Route('GET', 'me/player/devices')
		return await self.request(r)

	async def player_next(self, device_id):
		r = Route('POST', 'me/player/next', device=device_id)
		await self.request(r)

	async def player_prev(self, device_id):
		r = Route('POST', 'me/player/previous', device=device_id)
		await self.request(r)

	async def player_play(self, device_id, **kwargs):
		r = Route('PUT', 'me/player/play', device=device_id)
		await self.request(r, json=kwargs)

	async def player_pause(self, device_id):
		r = Route('PUT', 'me/player/pause', device=device_id)
		await self.request(r)

	async def player_seek(self, time, device_id):
		query = dict(position_ms=time)
		if device_id is not None:
			query['device'] = device_id
		r = Route('PUT', 'me/player/seek', **query)
		await self.request(r)

	async def player_repeat(self, state, device_id):
		query = dict(state=state)
		if device_id is not None:
			query['device'] = device_id
		r = Route('PUT', 'me/player/repeat', **query)
		await self.request(r)

	async def player_volume(self, volume, device_id):
		query = dict(volume_percent=volume)
		if device_id is not None:
			query['device'] = device_id
		r = Route('PUT', 'me/player/volume', **query)
		await self.request(r)

	async def player_shuffle(self, state, device_id):
		query = dict(state='true' if state else 'false')

		if device_id is not None:
			query['device'] = device_id

		r = Route('PUT', 'me/player/shuffle', **query)
		await self.request(r)

	async def search(self, q, type, **kwargs):
		r = Route('GET', 'search', type=type, q=q, **kwargs)
		return await self.request(r)

	async def get_me(self):
		r = Route('GET', 'me')
		return await self.request(r)

	async def get_me_top_tracks(self, **kwargs):
		r = Route('GET', 'me/top/tracks', **kwargs)
		return await self.request(r)

	async def get_me_top_artists(self, **kwargs):
		r = Route('GET', 'me/top/artists', **kwargs)
		return await self.request(r)

	async def get_playlist(self, playlist_id):
		r = Route('GET', 'playlists/{0}'.format(playlist_id))
		return await self.request(r)

	async def get_me_playlists(self):
		raise NotImplemented

	async def get_user_playlists(self, user_id):
		r = Route('GET', 'users/{0}/playlists'.format(user_id), limit=50)
		return await self.request(r)

	async def get_playlist_tracks(self, playlist_id):
		r = Route('GET', 'playlists/{0}/tracks'.format(playlist_id))
		return await self.request(r)

	async def playlist_add_tracks(self, playlist_id, **kwargs):
		data = dict(**filter_nones(kwargs))

		r = Route('POST', 'playlists/{0}/tracks'.format(playlist_id))
		return await self.request(r, json=data)

	async def create_playlist(self, user_id, name, **kwargs):
		data = dict(name=name, **filter_nones(kwargs))

		r = Route('POST', 'users/{0}/playlists'.format(user_id))
		return await self.request(r, json=data)

	async def edit_playlist(self, playlist_id, **kwargs):
		data = filter_nones(kwargs)

		r = Route('PUT', 'playlists/{0}'.format(playlist_id))
		await self.request(r, json=data)

	async def get_user(self, user_id):
		r = Route('GET', 'users/{0}'.format(user_id))
		return await self.request(r)

	async def get_track(self, track_id):
		r = Route('GET', 'tracks/{0}'.format(track_id))
		return await self.request(r)

	async def get_tracks(self, track_ids):
		r = Route('GET', 'tracks', ids=track_ids)
		return await self.request(r)

	async def get_audio_features(self, track_id):
		r = Route('GET', 'audio-features/{0}'.format(track_id))
		return await self.request(r)

	async def get_artist(self, artist_id):
		r = Route('GET', 'artists/{0}'.format(artist_id))
		return await self.request(r)

	async def get_artist_albums(self, artist_id, **kwargs):
		req = Route('GET', 'artists/{0}/albums'.format(artist_id), **kwargs)
		return await self.request(req)

	async def get_artists(self, artist_ids):
		r = Route('GET', 'artists', ids=artist_ids)
		return await self.request(r)

	async def get_artist_top_tracks(self, artist_id, **kwargs):
		r = Route('GET', 'artists/{0}/top-tracks'.format(artist_id), **kwargs)
		return await self.request(r)

	async def get_artist_related_artists(self, artist_id):
		r = Route('GET', 'artists/{0}/related-artists'.format(artist_id))
		return await self.request(r)

	async def get_album(self, album_id, **kwargs):
		r = Route('GET', 'albums/{0}'.format(album_id), **kwargs)
		return await self.request(r)

	async def get_albums(self, album_ids, **kwargs):
		r = Route('GET', 'albums', ids=album_ids, **kwargs)
		return await self.request(r)

	async def get_album_tracks(self, album_id, **kwargs):
		r = Route('GET', 'albums/{0}/tracks'.format(album_id), limit=50, **kwargs)
		return await self.request(r)

	async def get_followed_artists(self, type, **kwargs):
		r = Route('GET', 'me/following', type=type, **kwargs)
		return await self.request(r)

	async def following(self, type, ids, **kwargs):
		r = Route('PUT', 'me/following', type=type, ids=ids, **kwargs)
		await self.request(r)
