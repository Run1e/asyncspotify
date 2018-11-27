
def is_match(item, kwargs):
	for k, v in kwargs.items():
		if getattr(item, k, None) != v:
			return False
	return True

def get(items, **kwargs):
	for item in items:
		if is_match(item, kwargs):
			return item
	return None

def find(items, **kwargs):
	return filter(lambda item: is_match(item, kwargs), items)