import aiohttp
import logging

from asyncio import Lock, sleep
import json as jsonserial

from .exceptions import *

log = logging.getLogger(__name__)


class Route:
	BASE = 'https://api.spotify.com/v1'

	def __init__(self, method, url, **params):
		self.method = method
		self.url = url if url.startswith('http') else '{0}/{1}'.format(self.BASE, url)
		self.params = params

	def __repr__(self):
		return '<Route method={0.method} url={0.url}>'.format(self)


class HTTP:
	_attempts = 5
	_base = 'https://api.spotify.com/v1'

	def __init__(self, auth):
		self.auth = auth
		self.session = auth.session
		self.lock = Lock()

	def access_header(self):
		return dict(Authorization='Bearer {}'.format(self.auth.access_token))

	async def request(self, route, data=None, json=None, headers=None):

		if headers:
			headers.update(self.access_header())
		else:
			headers = self.access_header()

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

				async with self.session.request(**kw) as resp:
					status_code = resp.status
					headers = resp.headers
					text = await resp.text()

					try:
						data = jsonserial.loads(text)
					except jsonserial.JSONDecodeError:
						data = None

					if 200 <= status_code < 300:
						return data

					try:
						error = data['error']['message']
					except KeyError:
						error = None

					if status_code == 429:
						retry_after = int(headers.get('Retry-After', 1)) + 1
						log.warning('Rate limited. Retrying in {0} seconds.'.format(retry_after))
						await sleep(retry_after)
						continue

					elif status_code == 400:
						raise BadRequest(resp, error)

					elif status_code == 401:
						if error == 'The access token expired':
							await self.auth.refresh()
							kw['headers'].update(self.access_header())
							continue
						else:
							raise Unauthorized(resp, error)

					elif status_code == 403:
						raise Forbidden(resp, error)

					elif status_code == 404:
						raise NotFound(resp, error)

					elif status_code == 405:
						raise NotAllowed(resp, error)

					elif status_code >= 500:
						continue

		raise HTTPException(resp, 'Request failed 5 times.')

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

	async def search(self, types, query, limit, **kwargs):
		r = Route('GET', 'search', type=','.join(types), q=query, limit=limit, **kwargs)
		return await self.request(r)

	async def get_me(self):
		r = Route('GET', 'me')
		return await self.request(r)

	async def get_me_top_tracks(self, limit=20, offset=0, time_range='medium_term'):
		r = Route('GET', 'me/top/tracks', limit=limit, offset=offset, time_range=time_range)
		return await self.request(r)

	async def get_me_top_artists(self, limit=20, offset=0, time_range='medium_term'):
		r = Route('GET', 'me/top/artists', limit=limit, offset=offset, time_range=time_range)
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

	async def playlist_add_tracks(self, playlist_id, track_ids, position=0):
		req = Route('POST', 'playlists/{0}/tracks'.format(playlist_id))
		return await self.request(req, json=dict(uris=track_ids, position=position))

	async def create_playlist(self, user_id, name, description, public, collaborative):
		data = dict(
			name=name,
			description=description,
			public=public,
			collaborative=collaborative
		)

		r = Route('POST', 'users/{}/playlists'.format(user_id))

		return await self.request(r, json=data)

	async def edit_playlist(self, playlist_id, name, description, public, collaborative):
		new = dict()

		for key, value in dict(name=name, description=description, public=public, collaborative=collaborative).items():
			if value is not None:
				new[key] = value

		r = Route('PUT', 'playlists/{0}'.format(playlist_id))

		await self.request(r, json=new)

	async def get_user(self, user_id):
		r = Route('GET', 'users/{0}'.format(user_id))
		return await self.request(r)

	async def get_track(self, track_id):
		r = Route('GET', 'tracks/{0}'.format(track_id))
		return await self.request(r)

	async def get_tracks(self, track_ids):
		r = Route('GET', 'tracks', ids=','.join(track_ids))
		return await self.request(r)

	async def get_audio_features(self, track_id):
		r = Route('GET', 'audio-features/{0}'.format(track_id))
		return await self.request(r)

	async def get_artist(self, artist_id):
		r = Route('GET', 'artists/{0}'.format(artist_id))
		return await self.request(r)

	async def get_artist_albums(self, artist_id, limit=50, **kwargs):
		req = Route('GET', 'artists/{0}/albums'.format(artist_id), limit=limit, **kwargs)
		return await self.request(req)

	async def get_artists(self, artist_ids):
		r = Route('GET', 'artists', ids=','.join(artist_ids))
		return await self.request(r)

	async def get_artist_top_tracks(self, artist_id, market):
		r = Route('GET', 'artists/{0}/top-tracks'.format(artist_id), market=market)
		return await self.request(r)

	async def get_artist_related_artists(self, artist_id):
		r = Route('GET', 'artists/{0}/related-artists'.format(artist_id))
		return await self.request(r)

	async def get_album(self, album_id, **kwargs):
		r = Route('GET', 'albums/{0}'.format(album_id), **kwargs)
		return await self.request(r)

	async def get_albums(self, album_ids, **kwargs):
		r = Route('GET', 'albums', ids=','.join(album_ids), **kwargs)
		return await self.request(r)

	async def get_album_tracks(self, album_id, **kwargs):
		r = Route('GET', 'albums/{0}/tracks'.format(album_id), limit=50, **kwargs)
		return await self.request(r)

	async def get_followed_artists(self, type='artist', limit=50):
		r = Route('GET', 'me/following', type=type, limit=limit)
		return await self.request(r)

	async def following(self, type, ids, **kwargs):
		r = Route('PUT', 'me/following', type=type, ids=','.join(ids), **kwargs)
		await self.request(r)

	async def close_session(self):
		await self.session.close()
