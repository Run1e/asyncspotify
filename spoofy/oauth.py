
import aiohttp, asyncio, json, logging, base64
from urllib.parse import urlencode, urlparse, parse_qs


from .exceptions import AuthenticationError, RefreshTokenFailed


log = logging.getLogger(__name__)

class OAuth:
	'''Implements the Authorization Code Flow OAuth method.'''

	AUTHORIZE_URL = 'https://accounts.spotify.com/authorize'
	TOKEN_URL = 'https://accounts.spotify.com/api/token'

	def __init__(self, client_id, client_secret, redirect_uri, scope: tuple = None, session=None):
		
		self.client_id = client_id
		self.client_secret = client_secret
		self.redirect_uri = redirect_uri
		self.scope = scope
		self.response_type = 'code'
		self.session=session
	
	def create_auth_url(self):
		params = {
			'client_id': self.client_id,
			'redirect_uri': self.redirect_uri,
			'response_type': 'code',
		}
		
		if self.scope is not None:
			params['scope'] = ' '.join(self.scope)
	
		return f'{self.AUTHORIZE_URL}?{urlencode(params)}'
	
	async def open_auth(self, auth_url):
		import webbrowser
		webbrowser.open(auth_url)
		
	def get_code_from_redirect(self, url):
		query = urlparse(url).query
		return parse_qs(query)['code'][0]
		
	async def get_tokens(self, code):
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
			
			self.access_token = data['access_token']
			self.refresh_token = data['refresh_token']
			
			return self.access_token, self.refresh_token
		
	async def refresh(self):
		params = {
			'grant_type': 'refresh_token',
			'refresh_token': self.refresh_token,
			'client_id': self.client_id,
			'client_secret': self.client_secret
		}
		
		async with self.session.post(self.TOKEN_URL, data=params) as resp:
			data = json.loads(await resp.text())
				
			if resp.status != 200:
				raise RefreshTokenFailed(resp, data['error']['message'])
			
			self.access_token = data['access_token']