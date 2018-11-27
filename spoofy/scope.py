

class Scope:
	
	__slots__ = (
		'user_read_recently_played',
		'user_top_read',
		'user_follow_read',
		'user_follow_modify',
		'user_modify_playback_state',
		'user_read_playback_state',
		'user_read_currently_playing',
		'user_library_read',
		'user_library_modify',
		'user_read_private',
		'user_read_birthdate',
		'user_read_email',
		'playlist_modify_public',
		'playlist_read_collaborative',
		'playlist_modify_private',
		'playlist_read_private',
		'streaming',
		'app_remote_control'
	)
	
	def __init__(self, *args):
		for slot in self.__slots__:
			setattr(self, slot, slot in args or slot.replace('_', '-') in args)
	
	def __str__(self):
		return self.to_string()
	
	def to_string(self):
		out = ''
		for slot in filter(lambda s: getattr(self, s), self.__slots__):
			out += ' ' + slot.replace('_', '-')
		return out[1:]