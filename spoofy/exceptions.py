

class SpoofyException(Exception):
    def __str__(self):
        return 'Spoofy encountered an exception.'

class NoCredentialsFound(SpoofyException):
    def __str__(self):
        return 'No credentials found in cache file.'

class HTTPException(SpoofyException):
    def __init__(self, resp=None):
        self.status = resp.status
        self.reason = resp.reason
        self.method = resp.method

    def __repr__(self):
        return f'{self.method} failed: {self.status} {self.reason}'

    def __str__(self):
        return 'HTTP request failed.'

class AuthenticationError(HTTPException):
    def __str__(self):
        return 'Authentication failed.'

class RefreshTokenFailed(AuthenticationError):
    def __str__(self):
        return 'Token refresh failed.'

class Unauthorized(HTTPException):
    def __str__(self):
        return 'Access to resource requires authorization.'

class Forbidden(HTTPException):
    pass

class NotFound(HTTPException):
    pass