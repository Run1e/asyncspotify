
from math import ceil

def get(items, **kwargs):
	'''
	Get an item from a list of items.
	
	:param items: List or iterator containing :class:`Object` s
	:param kwargs: kwargs that should match with the objects attributes.
	:return: First item that matched.
	'''
	for item in items:
		if _is_match(item, kwargs):
			return item
	return None

def find(items, **kwargs):
	'''
	Same as :func:`get` except it returns a list of all matching items.
	
	:param items: List or iterator containing :class:`Object` s
	:param kwargs: kwargs that should match with the objects attributes.
	:return: List[:class:`Object`]
	'''
	return list(filter(lambda item: _is_match(item, kwargs), items))

def _is_match(item, kwargs):
	for k, v in kwargs.items():
		if getattr(item, k, None) != v:
			return False
	return True


class SliceIterator:
	def __init__(self, list, step):
		self.current = -1
		self.list = list
		self.step = step
		self.step_count = len(list) / step
	
	def __iter__(self):
		return self
	
	def __next__(self):
		self.current += 1
		base = self.current * self.step
		
		if self.current >= self.step_count:
			raise StopIteration
		
		return self.list[base:base + self.step]