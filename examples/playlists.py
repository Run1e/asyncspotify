# get a playlist
playlist = await sp.get_playlist('1wPvaRtuI8mt10CpP2KnlO')

# iterate tracks
for track in playlist.tracks:
	print(track)

# get the user we're logged in as
me = await sp.get_me()
# <PrivateUser id='runie13'>

# create a playlist
my_playlist = await me.create_playlist(name='My playlist!', description='This is the playlist description.')
# <FullPlaylist id='0FECu9cwvviV3rwOjDqU9j' name='My playlist!'>

# add tracks from the first playlist to newly created second playlist
await my_playlist.add_tracks(*playlist.tracks)