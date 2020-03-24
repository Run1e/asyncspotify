from datetime import timedelta

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

def convertToTimeDelta(data, listOfFieldsToConvert):
	'''
	Function to convert fields into timedelta objects

	:parm data: Dictionary containing lists of dicts or dicts or a mix of both
	:parm listOfFieldsToConvert: List of the fields that need to be converted into time delta objects 
	'''
	# Loop through primary keys in data
	for item in data:
		# Applies to all the primary keys except track. These only have start and duration keys so this might be able to be simplified
		if type(data[item]) == list:
			for field in listOfFieldsToConvert:
				# Check if the field exists in the list
				if data[item][0].get(field, None) != None:
					# Loop through each item in list, setting the field to a timedelta object
					for i in data[item]:
						i[field] = timedelta(seconds=i[field])
		elif type(data[item]) == dict:
			# Ignore the meta field
			if item != 'meta':
				for field in listOfFieldsToConvert:
					if data[item].get(field, None) != None:
						data[item][field] = timedelta(seconds=data[item][field])
	return data
