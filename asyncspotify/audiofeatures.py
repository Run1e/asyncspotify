from datetime import timedelta

from .object import Object


class AudioFeatures(Object):
	_type = 'audio_features'

	def __init__(self, client, data):
		super().__init__(client, data)

		self.acousticness = data.pop('acousticness')
		self.analysis_url = data.pop('analysis_url')
		self.danceability = data.pop('danceability')
		self.duration = timedelta(milliseconds=data.pop('duration_ms'))
		self.energy = data.pop('energy')
		self.instrumentalness = data.pop('instrumentalness')
		self.key = data.pop('key')
		self.liveness = data.pop('liveness')
		self.loudness = data.pop('loudness')
		self.mode = data.pop('mode')
		self.speechiness = data.pop('speechiness')
		self.tempo = data.pop('tempo')
		self.time_signature = data.pop('time_signature')
		self.track_href = data.pop('track_href')
		self.valence = data.pop('valence')
