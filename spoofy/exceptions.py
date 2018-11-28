

class SpoofyException(Exception):
	pass

class CheckFailure(SpoofyException):
	def __init__(self, check):
		super().__init__(f'Missing scope: \'{check}\'')

class NoCredentialsFound(SpoofyException):
	def __init__(self):
		super().__init__('No credentials found in cache file.')

class HTTPException(SpoofyException):
	def __init__(self, resp, message=None):
		self.response = resp
		self.message = message
		error = f'{resp.status} {resp.reason}'
		if message is not None:
			error += f' - {self.message}'
		super().__init__(error)

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

class NotAllowed(BadRequest):
	pass