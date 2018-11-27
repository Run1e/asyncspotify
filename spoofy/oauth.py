
import json, logging
from urllib.parse import urlencode, urlparse, parse_qs


from .exceptions import AuthenticationError, RefreshTokenFailed

cache_file = None

log = logging.getLogger(__name__)

class OAuth:
	'''Implements the Authorization Code Flow OAuth method.'''

	AUTHORIZE_URL = 'https://accounts.spotify.com/authorize'
	TOKEN_URL = 'https://accounts.spotify.com/api/token'

	_access_token = None
	_refresh_token = None

	def __init__(self, client_id, client_secret, redirect_uri, scope, session=None, on_update=None):
		
		self.client_id = client_id
		self.client_secret = client_secret
		self.redirect_uri = redirect_uri
		self.scope = scope
		self.response_type = 'code'
		self.session=session
		self.on_update = None
	
	@property
	def access_token(self):
		if self._access_token is None:
			raise AuthenticationError('Access token non-existent, authenticate first!')
		return self._access_token
	
	@property
	def refresh_token(self):
		if self._refresh_token is None:
			raise AuthenticationError('Refresh token non-existent, authenticate first!')
		return self._refresh_token
	
	def create_auth_url(self):
		params = dict(
			client_id=self.client_id,
			redirect_uri=self.redirect_uri,
			response_type='code'
		)
		
		params['scope'] = str(self.scope)
	
		return f'{self.AUTHORIZE_URL}?{urlencode(params)}'
	
	async def open_auth(self, auth_url):
		import webbrowser
		webbrowser.open(auth_url)
		
	def get_code_from_redirect(self, url):
		query = urlparse(url).query
		return parse_qs(query)['code'][0]
		
	async def get_tokens(self, code):
		params = dict(
			client_id=self.client_id,
			client_secret=self.client_secret,
			grant_type='authorization_code',
			code=code,
			redirect_uri=self.redirect_uri
		)
		
		async with self.session.post(self.TOKEN_URL, data=params) as resp:
			if resp.status != 200:
				raise AuthenticationError(resp)
			
			data = await resp.json()
			
			self._access_token = data['access_token']
			self._refresh_token = data['refresh_token']
			
			if self.on_update:
				self.on_update[0](self.on_update[1], self._access_token, self._refresh_token)
			
	async def refresh(self):
		params = dict(
			grant_type='refresh_token',
			refresh_token=self._refresh_token,
			client_id=self.client_id,
			client_secret=self.client_secret
		)
		
		async with self.session.post(self.TOKEN_URL, data=params) as resp:
			data = json.loads(await resp.text())
				
			if resp.status != 200:
				raise RefreshTokenFailed(resp, ': '.join(data.values()))
			
			self._access_token = data['access_token']
			
			if self.on_update:
				self.on_update[0](self.on_update[1], self._access_token, self._refresh_token)
	
def on_update_func(cache_file, access_token, refresh_token=None):
	with open(cache_file, 'w') as f:
		f.write(json.dumps({'access_token': access_token, 'refresh_token': refresh_token}))
				
async def easy_auth(auth, cache_file):
	import json
	
	auth.on_update = (on_update_func, cache_file)
	
	try:
		with open(cache_file, 'r') as f:
			data = json.loads(f.read())
			if 'access_token' in data and 'refresh_token' in data:
				auth._access_token = data['access_token']
				auth._refresh_token = data['refresh_token']
				return
	except FileNotFoundError:
		pass
		
	code_url = input(f'Please open this URL: {auth.create_auth_url()}\n- and then input the URL you were redirected to after accepting:\n')
	
	code = auth.get_code_from_redirect(code_url)
	
	await auth.get_tokens(code)