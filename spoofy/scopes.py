from .flags import Flag, Flags


class Scopes(Flags):
	ugc_image_upload = Flag(0)
	user_read_playback_state = Flag(1)
	user_modify_playback_state = Flag(2)
	user_read_currently_playing = Flag(3)
	streaming = Flag(4)
	app_remote_control = Flag(5)
	user_read_email = Flag(6)
	user_read_private = Flag(7)
	playlist_modify_public = Flag(8)
	playlist_read_private = Flag(9)
	playlist_modify_private = Flag(10)
	user_library_modify = Flag(11)
	user_library_read = Flag(12)
	user_top_read = Flag(13)
	user_read_recently_played = Flag(14)
	user_follow_read = Flag(15)
	user_follow_modify = Flag(16)

	def tuples(self):
		return tuple(name.replace('_', '-') for name, value in self)