from datetime import datetime, timedelta

from .device import Device
from .object import Object
from .track import FullTrack


class CurrentlyPlaying(Object):
	'''
	Represents a Currently Playing object.

	timestamp: datetime
		When the object information was created by the Spotify API.
	progress: timedelta
		How far into the current track the player is.
	is_playing: bool
		Whether the track is playing or not.
	track: :class:`Track`
		What track is currently playing, can be ``None``
	currently_playing_type: str
		What is currently playing, can be ``track``, ``episode``, ``ad`` or ``unknown``.
	'''

	def __init__(self, client, data):
		super().__init__(client, data)

		self.timestamp = datetime.utcfromtimestamp(data.pop('timestamp') / 1000)
		self.progress = timedelta(milliseconds=data.pop('progress_ms'))
		self.is_playing = data.pop('is_playing')

		trck = data.pop('item')
		if trck is not None:
			self.track = FullTrack(client, trck)
		else:
			self.track = None

		self.currently_playing_type = data.pop('currently_playing_type')


class CurrentlyPlayingContext(CurrentlyPlaying):
	'''
	Represents a Player object, extends :class:`CurrentlyPlaying`

	This type has some additional attributes not existent in :class:`CurrentlyPlaying`.

	device: :class:`Device`
		What device is owns this context.
	repeat_state: str
		The repeat state of the player. Can be ``off``, ``track`` or ``context``.
	shuffe_state: bool
		The shuffle state of the player. Can be ``True`` or ``False``.
	'''

	def __init__(self, client, data):
		super().__init__(client, data)

		self.device = Device(client, data.pop('device'))
		self.repeat_state = data.pop('repeat_state')
		self.shuffle_state = data.pop('shuffle_state')

	async def next(self):
		'''Skips to the next track.'''
		await self._client.player_next(device=self.device.id)

	async def prev(self):
		'''Goes to the previous track.'''
		await self._client.player_prev(device=self.device.id)

	async def play(self, **kwargs):
		'''
		Starts playback.

		:param kwargs: Body parameters of the request.

		.. code-block:: py

			player_play(
				context_uri='spotify:album:1Je1IMUlBXcx1Fz0WE7oPT',
				offset=dict(uri='spotify:track:1301WleyT98MSxVHPZCA6M'),
				position_ms=1000
			)
		'''

		await self._client.player_play(device=self.device.id, **kwargs)

	async def pause(self):
		'''Pauses playback.'''
		await self._client.player_pause(device=self.device.id)

	async def seek(self, time):
		'''
		Seeks to a specified time in the current track.

		:param time: timedelta object or milliseconds (integer)
		'''

		await self._client.player_seek(time=time, device=self.device.id)

	async def repeat(self, state):
		'''
		Set player repeat mode.

		:param str state: Can be 'track', 'context' or 'off'.
		'''

		await self._client.player_repeat(state=state, device=self.device.id)

	async def volume(self, volume):
		'''
		Set player volume.

		:param int volume: Value from 0 to 100.
		'''
		await self._client.player_volume(volume=volume, device=self.device.id)

	async def shuffle(self, state):
		'''
		Set player shuffle mode.

		:param bool state: Shuffle mode state.
		'''

		await self._client.player_shuffle(state=state, device=self.device.id)
