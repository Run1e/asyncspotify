

import aiohttp, asyncio, json, logging

from urllib.parse import urlencode

from pprint import saferepr

from .exceptions import *

log = logging.getLogger(__name__)

class Request:

	base = 'https://api.spotify.com/v1'

	def __init__(self, method, endpoint=None, id=None, query=None, data=None):
		self.method = method
		self.data = data
		self.id = id
		
		if endpoint:
			self.url = f'{self.base}/{endpoint}'
		
		self.headers = {
			'Authorization': f'Bearer {self.access_token}'
		}

		if id:
			self.url += '/' + id
			
		if query:
			self.url += '?' + urlencode(query)

	@classmethod
	def set_access_token(cls, access_token):
		setattr(cls, 'access_token', access_token)

	def set_header(self, header, value):
		self.headers[header] = value

class HTTP:

	max_attempts = 5

	def __init__(self, session=None):
		self.session = session

	def set_access_token(self, access_token):
		self._access_token = access_token
		Request.set_access_token(access_token)
		
	async def request(self, req, attempt=0):
		if attempt <= 5:
			async with self.session.request(req.method, req.url, data=req.data, headers=req.headers) as resp:
				log.debug(f'{resp.status} {resp.reason} - {req.method} {req.url}')
				
				data = await resp.text()
				error = None
				
				if resp.headers.get('Content-Type', '').startswith('application/json'):
					data = json.loads(data)
					try: error = data['error']['message']
					except: pass
				
				# success, return text or json
				if 300 > resp.status >= 200:
					return data
				
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
			raise HTTPException(req)

	async def get_playlist(self, playlist_id):
		return await self.request(Request('GET', 'playlists', id=playlist_id))
	
	async def playlist_add_tracks(self, playlist_id, track_ids, position=0):
		return await self.request(Request('POST', 'playlists/{}/tracks'.format(playlist_id),
										  query=dict(uris=','.join(track_ids), position=position)))
	
	async def get_user(self, user_id):
		return await self.request(Request('GET', 'users', id=user_id))
	
	async def get_track(self, track_id):
		return await self.request(Request('GET', 'tracks', id=track_id))
	
	async def get_tracks(self, track_ids):
		return await self.request(Request('GET', 'tracks', query=dict(ids=','.join(track_ids))))
	
	async def get_artist(self, artist_id):
		return await self.request(Request('GET', 'artists', id=artist_id))
	
	async def get_album(self, album_id):
		return await self.request(Request('GET', 'albums', id=album_id))
	
	async def get_albums(self, album_ids):
		return await self.request(Request('GET', 'albums', query=dict(ids=','.join(album_ids))))