from .flags import Flag, Flags


class Scope(Flags):
	'''
	Flags representing Spotify scopes.

	ugc_image_upload
		Write access to user-provided images.
	user_modify_playback_state
		Write access to a user’s playback state.
	user_read_playback_state
		Read access to a user’s player state.
	user_read_currently_playing
		Read access to a user’s currently playing content.
	user_top_read
		Read access to a user's top artists and tracks.
	user_read_playback_position
		Read access to a user’s playback position in a content.
	user_read_recently_played
		Read access to a user’s recently played tracks.
	user_library_modify
		Write/delete access to a user's "Your Music" library.
	user_library_read
		Read access to a user's "Your Music" library.
	user_follow_modify
		Write/delete access to the list of artists and other users that the user follows.
	user_follow_read
		Read access to the list of artists and other users that the user follows.
	playlist_read_private
		Read access to user's private playlists.
	playlist_modify_public
		Write access to a user's public playlists.
	playlist_modify_private
		Write access to a user's private playlists.
	playlist_read_collaborative
		Include collaborative playlists when requesting a user's playlists.
	user_read_private
		Read access to user’s subscription details (type of user account).
	user_read_email
		Read access to user’s email address.
	app_remote_control
		Remote control playback of Spotify. This scope is currently available to Spotify iOS and Android SDKs.
	streaming
		Control playback of a Spotify track. This scope is currently available to the Web Playback SDK. The user must have a Spotify Premium account.
	'''

	ugc_image_upload = Flag(0)

	user_modify_playback_state = Flag(1)
	user_read_playback_state = Flag(2)
	user_read_currently_playing = Flag(3)

	user_top_read = Flag(4)
	user_read_playback_position = Flag(5)
	user_read_recently_played = Flag(6)

	user_library_modify = Flag(7)
	user_library_read = Flag(8)

	user_follow_modify = Flag(9)
	user_follow_read = Flag(10)

	playlist_read_private = Flag(11)
	playlist_modify_public = Flag(12)
	playlist_modify_private = Flag(13)
	playlist_read_collaborative = Flag(14)

	user_read_private = Flag(15)
	user_read_email = Flag(16)

	app_remote_control = Flag(17)
	streaming = Flag(18)

	def string(self):
		'''Get a string representation of the enabled scopes. Used when authenticating.'''

		return ' '.join(name.replace('_', '-') for name, value in self if value)