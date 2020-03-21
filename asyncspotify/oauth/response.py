from datetime import datetime, timedelta


class AuthenticationResponse:
	access_token: str
	token_type: str
	expires_in: int
	created_at: datetime
	expires_at: datetime

	def __init__(self, data):
		self.access_token = data.get('access_token')
		self.token_type = data.get('token_type')
		self.expires_in = data.get('expires_in')

		self.created_at = datetime.utcnow()
		self.expires_at = self.created_at + timedelta(seconds=self.expires_in)

	def to_dict(self):
		return dict(
			access_token=self.access_token,
			token_type=self.token_type,
			expires_in=self.expires_in,
		)

	def is_expired(self):
		return datetime.utcnow() > self.expires_at

	def seconds_until_expire(self):
		return (self.expires_at - datetime.utcnow()).total_seconds()


class AuthorizationCodeFlowResponse(AuthenticationResponse):
	scope: str
	refresh_token: str

	def __init__(self, data):
		super().__init__(data)
		self.scope = data.get('scope')
		self.refresh_token = data.get('refresh_token', None)  # can be none during refresh!

	def to_dict(self):
		data = super().to_dict()

		data.update(
			scope=self.scope,
			refresh_token=self.refresh_token,
		)

		return data


class EasyCodeFlowResponse(AuthorizationCodeFlowResponse):
	created_at: datetime
	expires_at: datetime

	def __init__(self, data):
		super().__init__(data)
		self.created_at = datetime.utcnow()
		self.expires_at = self.created_at + timedelta(seconds=self.expires_in)

	@classmethod
	def from_data(cls, data):
		self = cls(data)

		self.created_at = datetime.fromisoformat(data.get('created_at'))
		self.expires_at = datetime.fromisoformat(data.get('expires_at'))

		return self

	def to_dict(self):
		data = super().to_dict()

		data.update(
			created_at=self.created_at.isoformat(),
			expires_at=self.expires_at.isoformat()
		)

		return data

	def is_expired(self):
		return datetime.utcnow() > self.expires_at

	def seconds_until_expire(self):
		return (self.expires_at - datetime.utcnow()).total_seconds()
