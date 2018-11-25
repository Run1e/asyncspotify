from .http import Request

from pprint import pprint

class Pager:
	def __init__(self, http, obj):
		self.http = http
		self.current = -1
		self.set_batch(obj)
		
	def set_batch(self, obj):
		self.total = obj['total']
		self.next = obj['next']
		self.items = obj['items']
		self.limit = obj['limit']
		self.offset = obj['offset']
		
	async def get_next(self):
		req = Request('GET')
		req.url = self.next
		obj = await self.http.request(req)
		self.set_batch(obj)
	
	async def __aiter__(self):
		return self
	
	async def __anext__(self):
		self.current += 1
		current = self.current % self.limit
		if self.current >= self.total:
			raise StopAsyncIteration
		if current == 0 and self.current > 0:
			await self.get_next()
		return self.items[current]