class SpotifyException(Exception):
	'''
	Base exception of all exceptions thrown by this library.
	'''
	pass


class AuthenticationError(SpotifyException):
	'''
	General exception when authenticating failed.
	'''


class HTTPException(SpotifyException):
	'''
	Base exception of all HTTP related exceptions.

	response: aiohttp.ClientResponse
		The response of the failed HTTP request.
	message: Optional[str]
		Message about what went wrong.

	'''

	def __init__(self, response, message=None):
		self.response = response
		self.message = message

		error = '{0.status} {0.reason}'.format(response)

		if message is not None:
			error += ': {}'.format(self.message)

		super().__init__(error)


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
