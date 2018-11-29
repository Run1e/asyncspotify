from .exceptions import Unauthorized, CheckFailure

def token(coro):
	async def ensure_token(self, *args, **kwargs):
		try:
			return await coro(self, *args, **kwargs)
		except Unauthorized as exc:
			if exc.message == 'The access token expired':
				await self.refresh_token()
				return await coro(self, *args, **kwargs)
			else:
				raise
	
	return ensure_token

def getids(method):
	async def ensure_ids(self, *args, **kwargs):
		from .object import Object
		new_args = []
		new_kwargs = {}
		for index, arg in enumerate(args):
			new_args.append(arg.id if isinstance(arg, Object) else arg)
		for key, value in kwargs.items():
			new_kwargs[key] = value.id if isinstance(value, Object) else value
		return await method(self, *new_args, **new_kwargs)
	
	return ensure_ids


def check(scope):
	def create_check(method):
		async def check_deco(self, *args, **kwargs):
			if getattr(self.auth.scope, scope, None):
				await method(self, *args, **kwargs)
			else:
				raise CheckFailure(scope)
		return check_deco
	return create_check
			
"""
def cache(init):
	def cacher_func(self, *args, **kwargs):
		asd = Cacher.return_exists(self)
		if asd is not None:
			return asd
		else:
			init(self, *args, **kwargs)
			Cacher.on_object_create(self)
	return cacher_func
"""