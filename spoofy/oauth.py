import asyncio
import json
import logging
from datetime import datetime, timedelta
from urllib.parse import parse_qs, urlparse

from .http import Route
from .scope import Scope

log = logging.getLogger(__name__)


class Response:
	access_token: str
	token_type: str
	expires_in: int
	created_at: datetime
	expires_at: datetime

	def is_expired(self):
		return datetime.utcnow() > self.expires_at

	def seconds_until_expire(self):
		return (self.expires_at - datetime.utcnow()).total_seconds()


class Authorizer:
	AUTHORIZE_URL = 'https://accounts.spotify.com/authorize'
	TOKEN_URL = 'https://accounts.spotify.com/api/token'

	_client = None
	response: Response = None

	def __init__(self, scope):
		if not isinstance(scope, Scope):
			raise TypeError('Scopes has to be of type spoofy.Scopes')
		self.scope = scope

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


class AuthorizationCodeFlowResponse(Response):
	def __init__(self, data):
		self.access_token = data.get('access_token')
		self.token_type = data.get('token_type')
		self.scope = data.get('scope')
		self.expires_in = data.get('expires_in')
		self.refresh_token = data.get('refresh_token')

		self.created_at = datetime.utcnow()
		self.expires_at = self.created_at + timedelta(seconds=self.expires_in)


class EasyAuthResponse(AuthorizationCodeFlowResponse):
	@classmethod
	def from_stored(cls, data):
		self = cls(data)

		self.created_at = datetime.fromisoformat(data.pop('created_at'))
		self.expires_at = datetime.fromisoformat(data.pop('expires_at'))

		return self


class AuthorizationCodeFlow(Authorizer):
	PARSE_ERROR = ValueError('Unable to get code from that redirect url.')

	response: AuthorizationCodeFlowResponse

	def __init__(self, scope, redirect_uri, callback, response_class=AuthorizationCodeFlowResponse):
		super().__init__(scope)
		self.redirect_uri = redirect_uri
		self.response_class = response_class
		self.refresh_task = None
		self.callback = callback

	async def refresh(self):
		if self.response is None:
			raise TypeError("Can't refresh access token without refresh token.")

		data = dict(
			grant_type='refresh_token',
			refresh_token=self.response.refresh_token,
			client_id=self.client.id,
			client_secret=self.client.secret
		)

		r = Route('POST', self.TOKEN_URL)
		data = await self.client.http.request(r, data=data, authorize=False)

		self.callback(data)

	def create_authorize_route(self):
		params = dict(
			client_id=self.client.id,
			redirect_uri=self.redirect_uri,
			response_type='code'
		)

		if self.scope is not None:
			params['scope'] = self.scope.scope()

		return Route('GET', self.AUTHORIZE_URL, **params)

	def create_token_route(self, code):
		data = dict(
			client_id=self.client.id,
			client_secret=self.client.secret,
			grant_type='authorization_code',
			code=code,
			redirect_uri=self.redirect_uri
		)

		return Route('POST', self.TOKEN_URL), data

	def get_code_from_redirect(self, url):
		parsed = urlparse(url.strip())
		query = parsed.query

		if not query:
			raise self.PARSE_ERROR

		qs = parse_qs(query)
		if 'code' not in qs:
			raise self.PARSE_ERROR

		return qs['code'][0]


class EasyAuth(AuthorizationCodeFlow):
	def __init__(self, scope=Scope.all(), store='tokens.json'):
		super().__init__(scope, 'http://localhost/', self.on_update, EasyAuthResponse)
		self.store = store

	async def init(self):
		fmt = (
			'Hi! This is the initial EasyAuth setup.\n\n'
			'Please open this URL:\n{0}\n\n'
			'and then input the URL you were redirected to after accepting here:\n'
		).format(str(self.create_authorize_route()))

		code_url = input(fmt)

		code = self.get_code_from_redirect(code_url)

		r, d = self.create_token_route(code)

		return await self.client.http.request(r, data=d, authorize=False)

	def close(self):
		if self.refresh_task is not None:
			self.refresh_task.cancel()

	async def authorize(self):
		try:
			with open(self.store, 'r') as f:
				data = json.loads(f.read())
				self.response = EasyAuthResponse.from_stored(data)
				self.refresh_in(self.response.seconds_until_expire())
		except (FileNotFoundError, json.JSONDecodeError):
			data = await self.init()
			self.on_update(data)

	def refresh_in(self, seconds):
		if self.refresh_task is not None:
			self.refresh_task.cancel()

		self.refresh_task = asyncio.create_task(self._refresh_in_meta(seconds))

	async def _refresh_in_meta(self, seconds):
		if seconds > 0:
			log.debug('Refreshing access token in %s seconds', seconds)
			await asyncio.sleep(seconds)
			log.debug('%s seconds passed, refreshing access token now', seconds)

		await self.refresh()

	def on_update(self, data):
		if isinstance(self.response, Response):
			data['refresh_token'] = self.response.refresh_token

		resp = EasyAuthResponse(data)

		data['created_at'] = resp.created_at.isoformat()
		data['expires_at'] = resp.expires_at.isoformat()

		with open(self.store, 'w') as f:
			f.write(json.dumps(data, indent=2))

		self.response = resp

		self.refresh_in(resp.seconds_until_expire())
