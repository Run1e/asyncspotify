from datetime import timedelta
from .object import Object

class AudioAnalysis(Object):
	_type = 'audio_analysis'

	def __init__(self, client, data):
		super().__init__(client, data)
		self.bars = data.pop('bars')
		self.track = data.pop('track')
		self.beats = data.pop('beats')
		self.tatums = data.pop('tatums')
		self.sections = data.pop('sections')
		self.segments = data.pop('segments')