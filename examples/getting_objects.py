track = await sp.get_track('track_id')
# <FullTrack id='track_id' name='track name here'>

album = await sp.get_artist('artist_id')
# <FullArtist id='artist_id' name='artist name here'>

# and so on for playlists and albums...

# to get several instances:

albums = await sp.get_albums('album_id_1', 'album_id_2')
# [<FullAlbum id='album_id_1' ...>, <FullAlbum id='album_id_2' ...>]