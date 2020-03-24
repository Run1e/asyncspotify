import logging
from json import JSONDecodeError, dumps, loads
from os.path import isfile
from urllib.parse import parse_qs, urlparse

from .mixins import RefreshableFlowMixin
from .response import AuthenticationResponse, AuthorizationCodeFlowResponse
from ..http import Route
from ..scope import Scope

log = logging.getLogger(__name__)

AUTHORIZE_URL = 'https://accounts.spotify.com/authorize'
TOKEN_URL = 'https://accounts.spotify.com/api/token'


class Authenticator:
	'''Base authentication class. All authenticators should inherit from this, custom or not.'''

	_client = None
	_data: AuthenticationResponse = None

	def __init__(self, client_id, client_secret=None):
		self.client_id = client_id
		self.client_secret = client_secret

	def __call__(self, client):
		self._client = client
		return self

	async def close(self):
		pass

	@property
	def header(self):
		if self._data is None:
			raise ValueError('Not authorized yet, no Authorization header to craft')
		return self._data.header

	@property
	def client(self):
		if self._client is None:
			raise ValueError('Client not set for authenticator yet.')
		return self._client

	@property
	def market(self):
		raise RuntimeError('This authenticator does not ensure a market.')

	async def authorize(self):
		raise NotImplementedError


class ClientCredentialsFlow(Authenticator, RefreshableFlowMixin):
	'''
	Implements the Client Credentials flow.

	You can only access public resources using this authenticator.
	'''

	def __init__(self, client_id, client_secret, response_class=AuthenticationResponse):
		super().__init__(client_id, client_secret)
		self.response_class = response_class

	@property
	def market(self):
		# TODO: ??? does this make sense to do? I have no idea.
		return 'US'

	async def authorize(self):
		'''Authorize using this authenticator.'''

		await self.refresh(start_task=True)

	async def token(self):
		d = dict(
			grant_type='client_credentials',
			client_id=self.client_id,
			client_secret=self.client_secret
		)

		data = await self._token(d)

		return AuthenticationResponse(data)


class AuthorizationCodeFlow(Authenticator, RefreshableFlowMixin):
	'''
	Implements the Authorization Code flow.

	.. note::
	   This class is not for general use, please use :class:`EasyAuthorizationCodeFlow` or subclass this and implement
	   your own load(), store(response) and setup() methods.

	client_id: str
		Your application client id.
	client_secret: str
		Your application client secret.
	scope: :class:`Scope`
		The scope you're requesting.
	redirect_uri: str
		Where the user will be redirected to after accepting the client.
	response_class:
		The type that is expected to be returned from load() and setup(), and is passed to store(response) when a token refresh happens.
		Should be :class:`AuthorizationCodeFlowResponse` or inherit from it.
	'''

	_data: AuthorizationCodeFlowResponse

	def __init__(self, client_id, client_secret, scope, redirect_uri, response_class=AuthorizationCodeFlowResponse):
		super().__init__(client_id, client_secret)

		assert isinstance(scope, Scope)

		self.scope = scope
		self.redirect_uri = redirect_uri
		self.response_class = response_class

	@property
	def market(self):
		return 'from_token'

	async def token(self):
		if self._data is None:
			raise ValueError('Can\'t refresh token without previous refresh token')

		data = dict(
			grant_type='refresh_token',
			refresh_token=self._data.refresh_token,
			client_id=self.client_id,
			client_secret=self.client_secret
		)

		data = await self._token(data)

		ins = self.response_class(data)
		ins.refresh_token = self._data.refresh_token

		return ins

	async def authorize(self):
		'''Authorize the client. Reads from the file specificed by `store`.'''

		data = await self.load()

		# no data found, run first time setup
		# get response class, pass it to .store
		if data is None:
			data = await self.setup()

			if isinstance(data, AuthenticationResponse):
				await self.store(data)

		if not isinstance(data, AuthenticationResponse):
			raise TypeError('setup() has to return an AuthenticationResponse')

		self._data = data

		# refresh it now if it's expired
		if self._data.is_expired():
			await self.refresh(start_task=True)
		else:
			# manually start refresh task if we didn't refresh on startup
			self.refresh_in(self._data.seconds_until_expire())

	async def setup(self):
		raise NotImplementedError

	async def store(self, response):
		raise NotImplementedError

	async def load(self):
		raise NotImplementedError

	def create_authorize_route(self):
		'''Craft the :class:`Route` for the user to use for authorizing the client.'''

		params = dict(
			client_id=self.client_id,
			redirect_uri=self.redirect_uri,
			response_type='code'
		)

		if self.scope is not None:
			params['scope'] = self.scope.string()

		return Route('GET', AUTHORIZE_URL, **params)

	def get_code_from_redirect(self, url):
		'''Extract the authorization code from the redirect uri.'''

		parsed = urlparse(url.strip())
		query = parsed.query

		if not query:
			raise ValueError('Unable to parse that redirect url')

		qs = parse_qs(query)
		if 'code' not in qs:
			raise ValueError('Redirect url seems to be missing code fragment')

		return qs['code'][0]

	def create_token_data_from_code(self, code):
		return dict(
			client_id=self.client_id,
			client_secret=self.client_secret,
			grant_type='authorization_code',
			code=code,
			redirect_uri=self.redirect_uri
		)


class EasyAuthorizationCodeFlow(AuthorizationCodeFlow):
	def __init__(self, client_id, client_secret, scope=Scope.none(), storage='secret.json', response_class=AuthorizationCodeFlowResponse):
		super().__init__(client_id, client_secret, scope, 'http://localhost/', response_class)
		self.storage = storage

	async def setup(self):
		fmt = (
			'Hi! This is the initial EasyAuthorizationCode setup.\n\n'
			'Please open this URL:\n{0}\n\n'
			'and then input the URL you were redirected to after accepting here:\n'
		).format(str(self.create_authorize_route()))

		code_url = input(fmt)

		code = self.get_code_from_redirect(code_url)
		d = self.create_token_data_from_code(code)

		data = await self._token(d)
		return self.response_class(data)

	async def load(self):
		if isfile(self.storage):
			# if storage file exists, read and deserialize it
			with open(self.storage, 'r') as f:
				try:
					raw_data = loads(f.read())
				except JSONDecodeError:
					return None

				# return the response instance
				return self.response_class.from_data(raw_data)

	async def store(self, response):
		# simply store the response as a dumped json dict
		with open(self.storage, 'w') as f:
			f.write(dumps(response.to_dict(), indent=2))
