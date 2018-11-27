from .object import Object
from .exceptions import Unauthorized

def token(method):
	async def ensure_token(self, *args, **kwargs):
		try:
			return await method(self, *args, **kwargs)
		except Unauthorized as exc:
			if exc.message == 'The access token expired':
				await self.refresh_token()
				return await method(self, *args, **kwargs)
			else:
				raise
	
	return ensure_token

def getids(method):
	async def ensure_ids(self, *args, **kwargs):
		for index, arg in enumerate(args):
			if isinstance(arg, Object):
				args[index] = arg.id
		for key, value in kwargs.items():
			if isinstance(value, Object):
				kwargs[key] = value.id
		return await method(self, *args, **kwargs)
	
	return ensure_ids