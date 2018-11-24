
import aiohttp, asyncio, json, logging, base64

from .exceptions import NoCredentialsFound, AuthenticationError

from urllib.parse import urlencode, urlparse, parse_qs

log = logging.getLogger(__name__)

class OAuth:

	AUTHORIZE_URL = 'https://accounts.spotify.com/authorize'
	TOKEN_URL = 'https://accounts.spotify.com/api/token'

	def __init__(self, client_id, client_secret, redirect_uri, scope: tuple = None, loop=None):
		
		self.client_id = client_id
		self.client_secret = client_secret
		self.redirect_uri = redirect_uri
		self.scope = scope
		self.response_type = 'code'
		
		self.session = aiohttp.ClientSession(loop=loop or asyncio.get_event_loop())
		
	async def authorize(self):
		params = {
			'client_id': self.client_id,
			'redirect_uri': self.redirect_uri,
			'response_type': 'code',
		}
		
		if self.scope is not None:
			params['scope'] = ' '.join(self.scope)
		
		import webbrowser
		webbrowser.open(f'{self.AUTHORIZE_URL}?{urlencode(params)}')
		
		url = input('Please copy in the URL you were redirected to:\n')
		
		query = urlparse(url).query
		code = parse_qs(query)['code'][0]
		
		print(code)
		
		params = {
			'client_id': self.client_id,
			'client_secret': self.client_secret,
			'grant_type': 'authorization_code',
			'code': code,
			'redirect_uri': self.redirect_uri
		}
		
		async with self.session.post(self.TOKEN_URL, data=params) as resp:
			if resp.status != 200:
				raise AuthenticationError(resp)
			
			data = await resp.json()
			await self.session.close()
			
			return data['access_token'], data['refresh_token'], data['expires_in']
		
		
