

import aiohttp, asyncio, json, logging

from urllib.parse import urlencode

from pprint import saferepr

from .exceptions import *

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

class Request:

	base = 'https://api.spotify.com/v1'

	def __init__(self, method, endpoint=None, id=None, query=None):
		self.method = method
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
			async with self.session.request(req.method, req.url, headers=req.headers) as resp:
				
				data = json.loads(await resp.text())
				
				log.info(saferepr(data))
		
				# success, return text or json
				if 300 > resp.status >= 200:
					return data
	
				message = data['error']['message']
				
				if resp.status == 400:
					raise BadRequest(resp, message)
				elif resp.status == 401:
					raise Unauthorized(resp, message)
				elif resp.status == 403:
					raise Forbidden(resp, message)
				elif resp.status == 404:
					raise NotFound(resp, message)
		else:
			raise HTTPException(req)

	async def get_playlist(self, playlist_id):
		return await self.request(Request('GET', 'playlists', id=playlist_id))
	
	async def get_track(self, track_id):
		return await self.request(Request('GET', 'tracks', id=track_id))
	
	async def get_tracks(self, track_ids):
		return await self.request(Request('GET', 'tracks', query={'ids': ','.join(track_ids)}))
	
	async def get_artist(self, artist_id):
		return await self.request(Request('GET', 'artists', id=artist_id))
	
	async def get_album(self, album_id):
		return await self.request(Request('GET', 'albums', id=album_id))