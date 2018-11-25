_tracks = []

def cache(init):
	def predicate(self, *args, **kwargs):
		init(self, *args, **kwargs)
		_tracks.append(self)
	return predicate