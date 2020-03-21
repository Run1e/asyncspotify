class Flag:
	def __init__(self, pos: int):
		self.mask = 1 << pos

	def __set__(self, obj, val):
		return obj._set_flag(self.mask, val)

	def __get__(self, instance, owner):
		return instance._get_flag(self.mask)


class Flags:
	def __init__(self, value=0, **kwargs):
		self._value = value

		if kwargs:
			for name, val in self:
				new_val = kwargs.pop(name, None)
				if new_val is not None:
					setattr(self, name, new_val)

		if kwargs:
			raise ValueError('kwarg(s) does not have an associated flag: {0}'.format(', '.join(kwargs)))

	def __repr__(self):
		return '<%s value=%s>' % (self.__class__.__name__, self._value)

	def __iter__(self):
		for attr, flag in self.__class__.__dict__.items():
			if isinstance(flag, Flag):
				yield attr, self._get_flag(flag.mask)

	@classmethod
	def all(cls):
		obj = cls()
		for name, value in obj:
			setattr(obj, name, True)
		return obj

	@classmethod
	def none(cls):
		return cls(0b0)

	def _set_flag(self, mask: int, toggle):
		if toggle:
			self._value |= mask
		else:
			self._value &= ~mask

	def _get_flag(self, mask):
		return bool(self._value & mask)
