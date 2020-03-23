import logging

from .http import Route

log = logging.getLogger(__name__)


class Pager:
	def __init__(self, http, pager_object, self_limit=None):
		self.http = http
		self.pos = 0
		self.self_limit = self_limit
		self.set_next(pager_object)

	def set_next(self, obj):
		self.total = obj['total']
		self.next = obj['next']
		self.items = obj['items']
		self.limit = obj['limit']
		self.offset = obj['offset']

	async def get_next(self):
		r = Route('GET', self.next)
		obj = await self.http.request(r)
		self.set_next(obj)

	def __aiter__(self):
		return self

	async def __anext__(self):
		# stop if we hit the pager total or the specified pager limit
		if self.pos >= self.total or self.pos >= self.limit:
			raise StopAsyncIteration

		if self.self_limit is not None and self.pos >= self.self_limit:
			raise StopAsyncIteration

		# get the next page if we're exhausted this one
		if self.pos >= self.offset + self.limit:
			await self.get_next()

		item = self.items[self.pos - self.offset]
		self.pos += 1
		return item


class SearchPager(Pager):
	def __init__(self, http, obj, type, self_limit=None):
		self.type = type
		super().__init__(http, obj, self_limit)

	def set_next(self, obj):
		obj = obj[self.type]
		super().set_next(obj)


class CursorBasedPaging(SearchPager):
	def set_next(self, obj):
		obj[self.type]['offset'] = None
		self.cursors = obj[self.type]['cursors']
		super().set_next(obj)
