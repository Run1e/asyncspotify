import asyncio
import json
import logging
from urllib.parse import parse_qs, urlparse

from spoofy.http import Route
from spoofy.scope import Scope
from .response import AuthorizationCodeFlowResponse, AuthenticationResponse, EasyCodeFlowResponse
from .mixins import RefreshableMixin

log = logging.getLogger(__name__)

AUTHORIZE_URL = 'https://accounts.spotify.com/authorize'
TOKEN_URL = 'https://accounts.spotify.com/api/token'


class Authorizer:
	_client = None
	response: AuthenticationResponse = None

	@property
	def client(self):
		if self._client is None:
			raise ValueError('Authorizer has not been given a client yet.')
		return self._client

	def close(self):
		pass

	def header(self):
		if self.response is None:
			return None
		return dict(Authorization='%s %s' % (self.response.token_type, self.response.access_token))

	def set_client(self, client):
		self._client = client


class AuthorizationCodeFlow(Authorizer, RefreshableMixin):
	PARSE_ERROR = ValueError('Unable to get code from that redirect url.')

	def __init__(self, scope, redirect_uri, response_class=AuthorizationCodeFlowResponse):
		assert isinstance(scope, Scope)

		self.scope = scope
		self.redirect_uri = redirect_uri
		self.response_class = response_class
		self.refresh_task = None

	async def refresh(self):
		if self.response is None:
			raise TypeError("Can't refresh access token without refresh token.")

		data = dict(
			grant_type='refresh_token',
			refresh_token=self.response.refresh_token,
			client_id=self.client.id,
			client_secret=self.client.secret
		)

		print(data)

		r = Route('POST', TOKEN_URL)
		data = await self.client.http.request(r, data=data, authorize=False)

		data['expires_in'] = 4

		ins = self.response_class(data)
		ins.refresh_token = self.response.refresh_token
		return ins

	def create_authorize_route(self):
		params = dict(
			client_id=self.client.id,
			redirect_uri=self.redirect_uri,
			response_type='code'
		)

		if self.scope is not None:
			params['scope'] = self.scope.string()

		return Route('GET', AUTHORIZE_URL, **params)

	def create_token_route(self, code):
		data = dict(
			client_id=self.client.id,
			client_secret=self.client.secret,
			grant_type='authorization_code',
			code=code,
			redirect_uri=self.redirect_uri
		)

		return Route('POST', TOKEN_URL), data

	def get_code_from_redirect(self, url):
		parsed = urlparse(url.strip())
		query = parsed.query

		if not query:
			raise self.PARSE_ERROR

		qs = parse_qs(query)
		if 'code' not in qs:
			raise self.PARSE_ERROR

		return qs['code'][0]


class EasyCodeFlow(AuthorizationCodeFlow):
	def __init__(self, scope=Scope.all(), store='tokens.json'):
		super().__init__(scope, 'http://localhost/', EasyCodeFlowResponse)
		self.store = store

	async def init(self):
		fmt = (
			'Hi! This is the initial EasyCodeFlow setup.\n\n'
			'Please open this URL:\n{0}\n\n'
			'and then input the URL you were redirected to after accepting here:\n'
		).format(str(self.create_authorize_route()))

		code_url = input(fmt)

		code = self.get_code_from_redirect(code_url)

		r, d = self.create_token_route(code)
		data = await self.client.http.request(r, data=d, authorize=False)

		res = EasyCodeFlowResponse(data)

		self.on_refresh(res)
		self.response = res

		# start refresh task
		self.refresh_in(res.seconds_until_expire())

	def close(self):
		if self.refresh_task is not None:
			self.refresh_task.cancel()

	async def authorize(self):
		try:
			with open(self.store, 'r') as f:
				# load previous response from json data
				data = json.loads(f.read())
				self.response = self.response_class.from_data(data)

				# refresh it now if it's expired
				if self.response.seconds_until_expire() < 0:
					await self.dispatch_refresh()

				# start the refresh task
				self.refresh_in(self.response.seconds_until_expire())

		except (FileNotFoundError, json.JSONDecodeError):
			await self.init()

	def on_refresh(self, response: EasyCodeFlowResponse):
		with open(self.store, 'w') as f:
			f.write(json.dumps(response.to_dict(), indent=2))


class ClientCredentialsFlow(Authorizer, RefreshableMixin):
	async def authorize(self):
		response = await self.refresh()
		self.refresh_in(response.seconds_until_expire())
		self.response = response

	async def refresh(self):
		d = dict(
			grant_type='client_credentials',
			client_id=self.client.id,
			client_secret=self.client.secret
		)

		r = Route('POST', TOKEN_URL)
		data = await self.client.http.request(r, data=d, authorize=False)

		data['expires_in'] = 4

		return AuthenticationResponse(data)
