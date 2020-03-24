from .utils	import convertToTimeDelta
from .object import Object

class AudioAnalysis(Object):
	'''
	Class for Audio Analysis results from the Spotify API.
    
	'''
	_type = 'audio_analysis'

	def __init__(self, client, data):
		super().__init__(client, data)
		# List of seconds fields in data
		listOfFieldsToConvert = ['start','duration','offset_seconds','window_seconds','start_of_fade_out','loudness_max_time']
		data = convertToTimeDelta(data, listOfFieldsToConvert)
		self.bars = data.pop('bars')
		self.track = data.pop('track')
		self.beats = data.pop('beats')
		self.tatums = data.pop('tatums')
		self.sections = data.pop('sections')
		self.segments = data.pop('segments')

