import json
import logging
from urllib.parse import parse_qs, urlparse

from .mixins import RefreshableMixin
from .response import AuthenticationResponse, AuthorizationCodeFlowResponse, EasyCodeFlowResponse
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

	@property
	def header(self):
		if self._data is None:
			raise ValueError('Not authorized yet, no Authorization header to craft')
		return dict(Authorization='%s %s' % (self._data.token_type, self._data.access_token))

	@property
	def client(self):
		if self._client is None:
			raise ValueError('Client not set for authorizer yet.')
		return self._client

	async def authorize(self):
		raise NotImplementedError


class AuthorizationCodeFlow(Authenticator, RefreshableMixin):
	'''Implements the Authorization Code flow. Subclass this or use EasyCodeFlow if you want persistent token storage.'''

	_data: AuthorizationCodeFlowResponse

	PARSE_ERROR = ValueError('Unable to get code from that redirect url')

	def __init__(self, client_id, client_secret, scope, redirect_uri, response_class=AuthorizationCodeFlowResponse):
		assert isinstance(scope, Scope)

		super().__init__(client_id, client_secret)

		self.scope = scope
		self.redirect_uri = redirect_uri
		self.response_class = response_class
		self.refresh_task = None

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
			raise self.PARSE_ERROR

		qs = parse_qs(query)
		if 'code' not in qs:
			raise self.PARSE_ERROR

		return qs['code'][0]


class EasyCodeFlow(AuthorizationCodeFlow):
	'''
	Convenience class that implements the Authorization Code flow in addition to simple token storage.

	client_id: str
		Your application client id.
	client_secret: str
		Your application client secret.
	scope: :class:`Scope`
		The scope you're requesting.
	store: str
		Where you want the tokens and metadata to be stored (in json format!)
	'''

	_data: EasyCodeFlowResponse

	def __init__(self, client_id, client_secret, scope=Scope.none(), store='tokens.json'):
		super().__init__(client_id, client_secret, scope, 'http://localhost/', EasyCodeFlowResponse)
		self.store = store

	async def init(self):
		fmt = (
			'Hi! This is the initial EasyCodeFlow setup.\n\n'
			'Please open this URL:\n{0}\n\n'
			'and then input the URL you were redirected to after accepting here:\n'
		).format(str(self.create_authorize_route()))

		code_url = input(fmt)

		code = self.get_code_from_redirect(code_url)

		d = dict(
			client_id=self.client_id,
			client_secret=self.client_secret,
			grant_type='authorization_code',
			code=code,
			redirect_uri=self.redirect_uri
		)

		data = await self._token(d)

		res = EasyCodeFlowResponse(data)
		self._data = res
		self.on_refresh(res)

		# start refresh task
		self._refresh_in(res.seconds_until_expire())

	def close(self):
		if self.refresh_task is not None:
			self.refresh_task.cancel()

	async def authorize(self):
		'''
		Authorize the client. Reads from the file specificed by `store`.

		:return:
		'''

		try:
			with open(self.store, 'r') as f:
				# load previous response from json data
				data = json.loads(f.read())
				self._data = self.response_class.from_data(data)

				# refresh it now if it's expired
				if self._data.seconds_until_expire() < 0:
					await self.refresh(start_task=True)
				else:
					# manually start refresh task if we didn't refresh on startup
					self._refresh_in(self._data.seconds_until_expire())

		except (FileNotFoundError, json.JSONDecodeError):
			await self.init()

	def on_refresh(self, response: EasyCodeFlowResponse):
		with open(self.store, 'w') as f:
			f.write(json.dumps(response.to_dict(), indent=2))


class ClientCredentialsFlow(Authenticator, RefreshableMixin):
	'''
	Implements the Client Credentials flow.

	You can only access public resources using this authenticator.
	'''

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
