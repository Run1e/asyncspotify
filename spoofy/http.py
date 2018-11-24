

import aiohttp, asyncio, json, logging

from .exceptions import *

log = logging.getLogger(__name__)

class Request:

	base = 'https://api.spotify.com/v1'

	def __init__(self, method, endpoint, id=None):
		self.method = method
		self.id = id
		self.url = f'{self.base}/{endpoint}'

		if id:
			self.url += '/' + id

	@classmethod
	def set_access_token(cls, access_token):
		setattr(cls, 'access_token', access_token)

	def set_header(self, header, value):
		self.headers[header] = value

class HTTP:

	max_attempts = 5

	def __init__(self, client, loop=None):
		self.client = client
		self.session = aiohttp.ClientSession(loop=loop or asyncio.get_event_loop())

	async def refresh_token(self, refresh_token):
		pass
	
	@property
	def headers(self):
		return {
			'Authorization': f'Bearer {self.client.access_token}'
		}

	async def request(self, req, attempt=1):
		async with self.session.request(req.method, req.url, headers=self.headers) as resp:

			# success, return text or json
			if 300 > resp.status >= 200:
				data = await resp.text(encoding='utf-8')
				if resp.headers['Content-Type'].startswith('application/json'):
					return json.loads(data)
				return data


			# unauth
			elif resp.status == 401:
				raise Unauthorized(resp)
			elif resp.status == 403:
				raise Forbidden(resp)
			elif resp.status == 404:
				raise NotFound(resp)

	async def get_playlist(self, playlist_id):
		return await self.request(Request('GET', 'playlists', id=playlist_id))