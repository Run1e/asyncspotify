class SpoofyException(Exception):
	'''
	Base exception of all exceptions thrown by this library.
	'''
	pass


class CheckFailure(SpoofyException):
	def __init__(self, check):
		super().__init__(f'Missing scope: \'{check}\'')


class NoCredentialsFound(SpoofyException):
	def __init__(self):
		super().__init__('No credentials found in cache file.')


class HTTPException(SpoofyException):
	'''
	Base exception of all HTTP related exceptions.
	'''

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
	'''
	400 Bad Request
	
	Base class for all 4xx status code exceptions.
	'''
	pass


class Unauthorized(BadRequest):
	'''
	401 Unauthorized
	'''
	pass


class Forbidden(BadRequest):
	'''
	403 Forbidden
	'''
	pass


class NotFound(BadRequest):
	'''
	404 Not Found
	'''
	pass


class NotAllowed(BadRequest):
	'''
	405 Method Not Allowed
	'''
	pass
