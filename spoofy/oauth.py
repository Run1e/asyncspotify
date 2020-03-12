from urllib.parse import parse_qs, urlencode, urlparse

import aiohttp
import asyncio
import json
import logging

from .exceptions import AuthenticationError

log = logging.getLogger(__name__)


class OAuth:
	'''Implements the Authorization Code Flow OAuth method.'''

	AUTHORIZE_URL = 'https://accounts.spotify.com/authorize'
	TOKEN_URL = 'https://accounts.spotify.com/api/token'

	_access_token = None
	_refresh_token = None

	def __init__(self, client_id, client_secret, redirect_uri, scope=None, loop=None, on_update=None):

		self.client_id = client_id
		self.client_secret = client_secret
		self.redirect_uri = redirect_uri
		self.scope = scope
		self.response_type = 'code'
		self.on_update = on_update

		self.session = aiohttp.ClientSession(loop=loop or asyncio.get_event_loop())

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

		if self.scope is not None:
			params['scope'] = ' '.join(self.scope)

		return '{}?{}'.format(self.AUTHORIZE_URL, urlencode(params))

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

			if callable(self.on_update[0]):
				self.on_update[0](self.on_update[1], self._access_token, self._refresh_token)


def on_update_func(cache_file, access_token, refresh_token):
	with open(cache_file, 'w') as f:
		f.write(json.dumps({'access_token': access_token, 'refresh_token': refresh_token}))


async def easy_auth(client_id, client_secret, scope, cache_file):
	'''
	Convenience function to make authorization using the Authorization Code Flow method as easy as possible.
	
	.. note::
		The client id and client secret are just that, *secret*.
		The tokens stored in `cache_file` are also extremely sensitive, as they single-handedly gives access to your
		account until the token runs out.
	
	:param client_id: Client ID of your application.
	:param client_secret: Client Secret of your application.
	:param scope: List of scopes (listed `here. <https://developer.spotify.com/documentation/general/guides/scopes/>`_)
	:param cache_file: JSON file to store the access and refresh tokens in.
	:return:
	'''

	import json

	auth = OAuth(
		client_id=client_id,
		client_secret=client_secret,
		redirect_uri='http://localhost/',
		scope=scope,
	)

	auth.on_update = (on_update_func, cache_file)

	try:
		with open(cache_file, 'r') as f:
			data = json.loads(f.read())
			if 'access_token' in data and 'refresh_token' in data:
				auth._access_token = data['access_token']
				auth._refresh_token = data['refresh_token']
				return auth
	except FileNotFoundError:
		pass

	fmt = (
		'Hi! This is the initial easy_auth setup.\n\n'
		'Please open this URL: {}\n'
		'- and then input the URL you were redirected to after accepting here:\n'
	)

	code_url = input(fmt.format(auth.create_auth_url()))

	code = auth.get_code_from_redirect(code_url)

	await auth.get_tokens(code)

	return auth
