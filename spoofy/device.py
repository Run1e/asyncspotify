from .object import Object


class Device(Object):
	'''
	Represents a Device object.

	is_active: bool
		Whether this device is currently the active device.
	is_private_session: bool
		If the device session is private.
	is_restricted: bool
		Whether controlling this device is restricted. If this is ``true``, no API commands will work on it.
	name: str
		Name of this device.
	type: str
		Equal to ``device``.
	volume_percent: int
		Volume of this device. Integer between 0 to 100.
	'''

	_type = 'device'

	def __init__(self, client, data):
		super().__init__(client, data)

		self.is_active = data.pop('is_active')
		self.is_private_session = data.pop('is_private_session')
		self.is_restricted = data.pop('is_restricted')
		self.volume_percent = data.pop('volume_percent')
