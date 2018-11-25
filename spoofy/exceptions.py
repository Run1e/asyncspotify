

class SpoofyException(Exception):
	pass

class NoCredentialsFound(SpoofyException):
	def __init__(self):
		super().__init__('No credentials found in cache file.')

class HTTPException(SpoofyException):
	def __init__(self, resp, message=None):
		self.response = resp
		self.message = message
		super().__init__(f'{resp.status} {resp.reason} - {message}')

class AuthenticationError(HTTPException):
	pass

class RefreshTokenFailed(AuthenticationError):
	pass

class BadRequest(HTTPException):
	pass

class Unauthorized(BadRequest):
	pass
	
class Forbidden(BadRequest):
	pass

class NotFound(BadRequest):
	pass