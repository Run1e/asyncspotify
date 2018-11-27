
def get(items, **kwargs):
	for item in items:
		if _is_match(item, kwargs):
			return item
	return None

def find(items, **kwargs):
	return list(filter(lambda item: _is_match(item, kwargs), items))

def _is_match(item, kwargs):
	for k, v in kwargs.items():
		if getattr(item, k, None) != v:
			return False
	return True