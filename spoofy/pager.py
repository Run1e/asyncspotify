import logging

from .http import Route

log = logging.getLogger(__name__)


class Pager:
	def __init__(self, http, pager_object, stop_after=None):
		self.http = http
		self.pos = 0
		self.stop_after = stop_after
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
		# stop if we hit the pager total
		if self.pos >= self.total:
			raise StopAsyncIteration

		if self.stop_after is not None and self.pos >= self.stop_after:
			raise StopAsyncIteration

		# get the next page if we're exhausted this one
		if self.pos >= self.offset + self.limit:
			await self.get_next()

		item = self.items[self.pos - self.offset]
		self.pos += 1
		return item


class SearchPager(Pager):
	def __init__(self, http, obj, type, stop_after=None):
		self.type = type
		super().__init__(http, obj, stop_after)

	def set_next(self, obj):
		obj = obj[self.type]
		super().set_next(obj)


class CursorBasedPaging(SearchPager):
	def set_next(self, obj):
		obj[self.type]['offset'] = None
		self.cursors = obj[self.type]['cursors']
		super().set_next(obj)
