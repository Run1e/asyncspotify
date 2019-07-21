import aiohttp, asyncio, logging

import json as jsonserial

from pprint import pprint

from .exceptions import *

log = logging.getLogger(__name__)


class Request:
	base = 'https://api.spotify.com/v1'
	access_token = None

	def __init__(self, method, endpoint=None, id=None, query=None, data=None, json=None, headers=None):
		self.method = method
		self.headers = {}
		self.params = query
		self.data = data
		self.json = json
		self.id = id

		if endpoint:
			self.url = '{}/{}'.format(self.base, endpoint)

		if isinstance(headers, dict):
			self.headers.update(headers)

		if id:
			self.url += '/' + id

	def set_header(self, header, value):
		self.headers[header] = value


class HTTP:
	max_attempts = 5

	def __init__(self, auth):
		self.auth = auth
		self.session = auth.session
		self.lock = asyncio.Event()

	async def request(self, req, attempt=0):
		if attempt <= 5:

			req.set_header('Authorization', 'Bearer {}'.format(self.auth.access_token))

			# stop new requests if a previous one caused a 429 which is still being awaited
			if self.lock.is_set():
				print('stopped!')
				await self.lock.wait()

			async with self.session.request(req.method, req.url, params=req.params, data=req.data, json=req.json,
											headers=req.headers) as resp:
				log.debug('{0.status} {0.reason} - {0.method} {0.url}'.format(resp))

				data = await resp.text()
				error = None

				if resp.headers.get('Content-Type', '').startswith('application/json'):
					data = jsonserial.loads(data)
					try:
						error = data['error']['message']
					except:
						pass

				# success, simply return data
				if 300 > resp.status >= 200:
					return data

				# rate limiting
				if resp.status == 429:
					self.lock.set()
					await asyncio.sleep(delay=int(resp.headers['Retry-After']) + 1)
					self.lock.clear()
					return await self.request(req, attempt + 1)

				if resp.status == 400:
					raise BadRequest(resp, error)
				elif resp.status == 401:
					if error == 'The access token expired':
						await self.auth.refresh()
						return await self.request(req, attempt + 1)
					else:
						raise Unauthorized(resp, error)
				elif resp.status == 403:
					raise Forbidden(resp, error)
				elif resp.status == 404:
					raise NotFound(resp, error)
				elif resp.status == 405:
					raise NotAllowed(resp, error)
		else:
			raise HTTPException(req, 'Request failed after 5 attempts.')

	async def get_player(self):
		return await self.request(Request('GET', 'me/player'))

	async def player_currently_playing(self):
		return await self.request(Request('GET', 'me/player/currently-playing'))

	async def get_devices(self):
		return await self.request(Request('GET', 'me/player/devices'))

	async def player_next(self, device_id):
		await self.request(Request('POST', 'me/player/next', query=dict(device=device_id) if device_id else None))

	async def player_prev(self, device_id):
		await self.request(Request('POST', 'me/player/previous', query=dict(device=device_id) if device_id else None))

	async def player_play(self, device_id):
		await self.request(Request('PUT', 'me/player/play', query=dict(device=device_id) if device_id else None))

	async def player_pause(self, device_id):
		await self.request(Request('PUT', 'me/player/pause', query=dict(device=device_id) if device_id else None))

	async def player_seek(self, time, device_id):
		query = dict(position_ms=time)
		if device_id is not None:
			query['device'] = device_id
		await self.request(Request('PUT', 'me/player/seek', query=query))

	async def player_repeat(self, state, device_id):
		query = dict(state=state)
		if device_id is not None:
			query['device'] = device_id
		await self.request(Request('PUT', 'me/player/repeat', query=query))

	async def player_volume(self, volume, device_id):
		query = dict(volume_percent=volume)
		if device_id is not None:
			query['device'] = device_id
		await self.request(Request('PUT', 'me/player/volume', query=query))

	async def player_shuffle(self, state, device_id):
		query = dict(state='true' if state else 'false')
		if device_id is not None:
			query['device'] = device_id

		await self.request(Request('PUT', 'me/player/shuffle', query=query))


	async def search(self, types, query, limit):
		return await self.request(Request('GET', 'search', query=dict(type=','.join(types),
																	  q=query, limit=limit)))

	async def get_me(self):
		return await self.request(Request('GET', 'me'))

	async def get_me_top_tracks(self, limit=20, offset=0):
		return await self.request(Request('GET', 'me/top/tracks', query=dict(limit=limit, offset=offset)))

	async def get_me_top_artists(self, limit=20, offset=0):
		return await self.request(Request('GET', 'me/top/artists', query=dict(limit=limit, offset=offset)))

	async def get_playlist(self, playlist_id):
		return await self.request(Request('GET', 'playlists', id=playlist_id))

	async def get_me_playlists(self):
		return

	async def get_user_playlists(self, user_id):
		return await self.request(Request('GET', 'users/{}/playlists'.format(user_id), query={'limit': 50}))

	async def get_playlist_tracks(self, playlist_id):
		return await self.request(Request('GET', 'playlists/{}/tracks'.format(playlist_id)))

	async def playlist_add_tracks(self, playlist_id, track_ids, position=0):
		return await self.request(Request('POST', 'playlists/{}/tracks'.format(playlist_id),
										  json=dict(uris=track_ids, position=position)))

	async def create_playlist(self, user_id, name, description, public, collaborative):
		data = dict(
			name=name,
			description=description,
			public=public,
			collaborative=collaborative
		)

		return await self.request(Request('POST', 'users/{}/playlists'.format(user_id),
										  headers={'Content-Type': 'application/json'},
										  json=data))

	async def edit_playlist(self, playlist_id, name, description, public, collaborative):
		new = {}
		for key, value in dict(name=name, description=description, public=public, collaborative=collaborative).items():
			if value is not None:
				new[key] = value

		await self.request(Request('PUT', 'playlists', id=playlist_id, json=new))

	async def get_user(self, user_id):
		return await self.request(Request('GET', 'users', id=user_id))

	async def get_track(self, track_id):
		return await self.request(Request('GET', 'tracks', id=track_id))

	async def get_tracks(self, track_ids):
		return await self.request(Request('GET', 'tracks', query=dict(ids=','.join(track_ids))))

	async def get_audio_features(self, track_id):
		return await self.request(Request('GET', 'audio-features/{}'.format(track_id)))

	async def get_artist(self, artist_id):
		return await self.request(Request('GET', 'artists', id=artist_id))

	async def get_artist_albums(self, artist_id, limit=50, **kwargs):
		return await self.request(Request('GET', 'artists/{}/albums'.format(artist_id), query=dict(limit=limit, **kwargs)))

	async def get_artists(self, artist_ids):
		return await self.request(Request('GET', 'artists', query=dict(ids=','.join(artist_ids))))

	async def get_artist_top_tracks(self, artist_id, market):
		return await self.request(Request('GET', 'artists/{}/top-tracks'.format(artist_id), query=dict(market=market)))

	async def get_artist_related_artists(self, artist_id):
		return await self.request(Request('GET', 'artists/{}/related-artists'.format(artist_id)))

	async def get_album(self, album_id):
		return await self.request(Request('GET', 'albums', id=album_id))

	async def get_albums(self, album_ids):
		return await self.request(Request('GET', 'albums', query=dict(ids=','.join(album_ids))))

	async def get_album_tracks(self, album_id):
		return await self.request(Request('GET', 'albums/{}/tracks'.format(album_id), query=dict(limit=50)))
