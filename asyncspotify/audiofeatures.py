from datetime import timedelta

from .object import SpotifyObject


class AudioFeatures(SpotifyObject):
	'''
	Represents an Audio Features object.

	id: str
		The Spotify ID of the track.
	uri: str
		Spotify URI of the album.
	analysis_url: str
		An HTTP URL to access the full audio analysis of this track.
	track_href: str
		A link to the Web API endpoint providing full details of the track.
	duration: timedelta
		The duration of the track.
	key: int
		The estimated overall key of the track.
	mode: int
		Mode indicates the modality (major or minor) of a track, the type of scale from which its melodic content is derived.
	time_signature: int
		An estimated overall time signature of a track.
	acousticness: float
		A confidence measure from 0.0 to 1.0 of whether the track is acoustic.
	danceability: float
		A measure of how suitable the track is for dancing.
	energy: float
		Energy is a measure from 0.0 to 1.0 and represents a perceptual measure of intensity and activity.
	instrumentalness: float
		Predicts whether a track contains no vocals.
	liveness: float
		Detects the presence of an audience in the recording.
	loudness: float
		The overall loudness of a track in decibels (dB).
	speechiness: float
		Speechiness detects the presence of spoken words in a track.
	valence: float
		A measure from 0.0 to 1.0 describing the musical positiveness conveyed by a track.
	tempo: float
		The overall estimated tempo of a track in beats per minute (BPM).
	'''

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
