from .http import Request

import logging

log = logging.getLogger(__name__)

class Pager:
	
	def __init__(self, http, obj):
		self.http = http
		self.current = -1
		self.set_batch(obj)
		log.debug(f'Pager created for {self.total} items')
		
	def set_batch(self, obj):
		self.total = obj['total']
		self.next = obj['next']
		self.items = obj['items']
		self.limit = obj['limit']
		self.offset = obj['offset']
		
	async def get_next(self):
		log.debug(f'Pager getting items {self.current}-{self.current + self.limit}')
		req = Request('GET')
		req.url = self.next
		obj = await self.http.request(req)
		self.set_batch(obj)
	
	def __aiter__(self):
		return self
	
	async def __anext__(self):
		self.current += 1
		current = self.current % self.limit
		if self.current >= self.total:
			raise StopAsyncIteration
		if current == 0 and self.current > 0:
			if self.next is None:
				raise StopAsyncIteration
			await self.get_next()
		return self.items[current]