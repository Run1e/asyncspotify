from .object import Object
from datetime import timedelta

class AudioAnalysis(Object):
	'''
	Class for Audio Analysis results from the Spotify API.
    
	'''
	_type = 'audio_analysis'

	def __init__(self, client, data):
		super().__init__(client, data)
		# Create list of the dicts in data['bars'] with start and duration converted to timedelta objects
		self.bars = [{
			'start': timedelta(seconds=bar.pop('start')), 
			'duration': timedelta(seconds=bar.pop('duration')), 
			**bar} 
			for bar in data['bars']
		] 
		self.beats = [{
			'start': timedelta(seconds=beat.pop('start')), 
			'duration': timedelta(seconds=beat.pop('duration')), 
			**beat} 
			for beat in data['beats']
		] 
		self.tatums = [{
			'start': timedelta(seconds=tatum.pop('start')), 
			'duration': timedelta(seconds=tatum.pop('duration')), 
			**tatum} 
			for tatum in data['tatums']
		] 
		self.sections = [{
			'start': timedelta(seconds=section.pop('start')), 
			'duration': timedelta(seconds=section.pop('duration')), 
			**section} 
			for section in data['sections']
		] 
		self.segments = [{
			'start': timedelta(seconds=segment.pop('start')), 
			'duration': timedelta(seconds=segment.pop('duration')), 
			'loudness_max_time': timedelta(seconds=segment.pop('loudness_max_time')),
			**segment} 
			for segment in data['segments']
		] 
		self.track = data.pop('track')
		self.track['duration'] = timedelta(seconds=self.track['duration'])
		self.track["offset_seconds"] = timedelta(seconds=self.track['offset_seconds'])
		self.track["window_seconds"] = timedelta(seconds=self.track['window_seconds'])
		self.track["end_of_fade_in"] = timedelta(seconds=self.track['end_of_fade_in'])
		self.track["start_of_fade_out"] = timedelta(seconds=self.track['start_of_fade_out'])
	