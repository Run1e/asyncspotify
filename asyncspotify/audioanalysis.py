from collections import namedtuple
from datetime import timedelta

from .object import SpotifyObject

TimeInterval = namedtuple('TimeInterval', ('start', 'duration', 'confidence'))

Section = namedtuple(
	'Section', (
		'start', 'duration', 'confidence',
		'loudness', 'tempo', 'tempo_confidence',
		'key', 'key_confidence', 'mode',
		'mode_confidence', 'time_signature', 'time_signature_confidence'
	)
)

Segment = namedtuple(
	'Segment', (
		'start', 'duration', 'confidence',
		'loudness_start', 'loudness_max', 'loudness_max_time',
		'loudness_end', 'pitches', 'timbre'
	)
)


Track = namedtuple(
	'Track', (
		'duration', 'sample_md5', 'offset_seconds',
		'window_seconds', 'analysis_sample_rate', 'analysis_channels',
		'end_of_fade_in', 'start_of_fade_out', 'loudness',
		'tempo', 'tempo_confidence', 'time_signature',
		'time_signature_confidence', 'key', 'key_confidence',
		'mode', 'mode_confidence', 'codestring',
		'code_version', 'echoprintstring', 'echoprint_version',
		'synchstring', 'synch_version', 'rhythmstring',
		'rhythm_version', 'num_samples'
	)
)


class AudioAnalysis(SpotifyObject):
	'''
	Represents an Audio Analysis object.

	This page only skims the details on this object. *Please* read the official Spotify documentation `here <https://developer.spotify.com/documentation/web-api/reference/tracks/get-audio-analysis/>`_.

	bars: List[TimeInterval]
		The time intervals of the bars throughout the track. A bar (or measure) is a segment of time defined as a given number of beats.
	beats: List[TimeInterval]
		The time intervals of beats throughout the track. A beat is the basic time unit of a piece of music; for example, each tick of a metronome.
	sections: List[Section]
		List of sections of the track. Sections are defined by large variations in rhythm or timbre, e.g. chorus, verse, bridge, guitar solo, etc.
	segments: List[Segment]
		List of audio segments of the track. Audio segments attempts to subdivide a song into many segments, with each segment containing a roughly consistent sound throughout its duration.
	tatums: List[TimeInterval]
		The time intervals of tatums throughout the track. A tatum represents the lowest regular pulse train that a listener intuitively infers from the timing of perceived musical events (segments).
	'''

	_type = 'audio_analysis'

	def __init__(self, client, data):
		super().__init__(client, data)

		self.bars = [
			TimeInterval(
				start=timedelta(seconds=bar.pop('start')),
				duration=timedelta(seconds=bar.pop('duration')),
				**bar
			) for bar in data.pop('bars')
		]

		self.beats = [
			TimeInterval(
				start=timedelta(seconds=beat.pop('start')),
				duration=timedelta(seconds=beat.pop('duration')),
				**beat
			) for beat in data.pop('beats')
		]

		self.tatums = [
			TimeInterval(
				start=timedelta(seconds=tatum.pop('start')),
				duration=timedelta(seconds=tatum.pop('duration')),
				**tatum
			) for tatum in data.pop('tatums')
		]

		self.sections = [
			Section(
				start=timedelta(seconds=section.pop('start')),
				duration=timedelta(seconds=section.pop('duration')),
				**section
			) for section in data.pop('sections')
		]

		self.segments = [
			Segment(
				start=timedelta(seconds=segment.pop('start')),
				duration=timedelta(seconds=segment.pop('duration')),
				loudness_max_time=timedelta(seconds=segment.pop('loudness_max_time')),
				loudness_end=segment.pop('loudness_end', None),  # can be None, apparently
				**segment
			) for segment in data.pop('segments')
		]

		track_data = data.pop('track')

		self.track = Track(
			duration=timedelta(seconds=track_data.pop('duration')),
			offset_seconds=timedelta(seconds=track_data.pop('offset_seconds')),
			window_seconds=timedelta(seconds=track_data.pop('window_seconds')),
			end_of_fade_in=timedelta(seconds=track_data.pop('end_of_fade_in')),
			start_of_fade_out=timedelta(seconds=track_data.pop('start_of_fade_out')),
			**track_data
		)
