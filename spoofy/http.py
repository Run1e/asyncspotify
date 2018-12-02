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
			self.url = f'{self.base}/{endpoint}'

		if self.access_token is not None:
			self.set_header('Authorization', f'Bearer {self.access_token}')

		if isinstance(headers, dict):
			self.headers.update(headers)

		if id:
			self.url += '/' + id

	@classmethod
	def set_access_token(cls, access_token):
		setattr(cls, 'access_token', access_token)

	def set_header(self, header, value):
		self.headers[header] = value


class HTTP:
	max_attempts = 5

	def __init__(self, session=None):
		self.session = session
		self.lock = asyncio.Event()

	def set_access_token(self, access_token):
		self._access_token = access_token
		Request.set_access_token(access_token)

	async def request(self, req, attempt=0):
		if attempt <= 5:

			# stop new requests if a previous one caused a 429 which is still being awaited
			if self.lock.is_set():
				print('stopped!')
				await self.lock.wait()

			async with self.session.request(req.method, req.url, params=req.params, data=req.data, json=req.json,
											headers=req.headers) as resp:
				log.debug(f'{resp.status} {resp.reason} - {req.method} {req.url}')

				data = await resp.text()
				error = None

				if resp.headers.get('Content-Type', '').startswith('application/json'):
					data = jsonserial.loads(data)
					try:
						error = data['error']['message']
					except:
						pass

				# success, return text or json
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
					raise Unauthorized(resp, error)
				elif resp.status == 403:
					raise Forbidden(resp, error)
				elif resp.status == 404:
					raise NotFound(resp, error)
				elif resp.status == 405:
					raise NotAllowed(resp, error)
		else:
			raise HTTPException(req, 'Request failed after 5 attempts.')

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
		return await self.request(Request('GET', f'users/{user_id}/playlists', query={'limit': 50}))

	async def get_playlist_tracks(self, playlist_id):
		return await self.request(Request('GET', f'playlists/{playlist_id}/tracks'))

	async def playlist_add_tracks(self, playlist_id, track_ids, position=0):
		return await self.request(Request('POST', f'playlists/{playlist_id}/tracks',
										  json=dict(uris=track_ids, position=position)))

	async def create_playlist(self, user_id, name, description, public, collaborative):
		data = dict(
			name=name,
			description=description,
			public=public,
			collaborative=collaborative
		)

		return await self.request(Request('POST', f'users/{user_id}/playlists',
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
		return await self.request(Request('GET', f'audio-features/{track_id}'))

	async def get_artist(self, artist_id):
		return await self.request(Request('GET', 'artists', id=artist_id))

	async def get_artists(self, artist_ids):
		return await self.request(Request('GET', 'artists', query=dict(ids=','.join(artist_ids))))

	async def get_album(self, album_id):
		return await self.request(Request('GET', 'albums', id=album_id))

	async def get_albums(self, album_ids):
		return await self.request(Request('GET', 'albums', query=dict(ids=','.join(album_ids))))

	async def get_album_tracks(self, album_id):
		return await self.request(Request('GET', f'albums/{album_id}/tracks', query=dict(limit=50)))
