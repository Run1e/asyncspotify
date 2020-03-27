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
	
	:param items: List or iterator containing :class:`Object`
	:param kwargs: kwargs that should match with the objects attributes.
	:return: List[:class:`Object`]
	'''
	return list(filter(lambda item: _is_match(item, kwargs), items))


def _is_match(item, kwargs):
	for k, v in kwargs.items():
		if getattr(item, k, None) != v:
			return False
	return True


def subslice(iter, step):
	group = []

	for idx, item in enumerate(iter):
		if idx % step == 0:
			if group:
				yield group
				group.clear()

		group.append(item)

	if group:
		yield group
