# get multiple tracks from query
tracks = await sp.search_tracks(q='involvers', limit=2)
# [<SimpleTrack id='5xoJhWwvzPJD9k8j8BE2xO' name='27'>, <SimpleTrack id='0WUTBejxPUhURFCFfSYbDc' name='Fighting My Fight'>]

# get *one* track from query
track = await sp.search_track(q='norton commander')
# <SimpleTrack id='5KZiiK8dvTgXaVnegsvvBz' name='Norton Commander (All We Need)'>

# get one album from query
album = await sp.search_album('hiatus kaiyote')
# <SimpleAlbum id='3qzmmmRmVBiOuMvrerfW4z' name='Choose Your Weapon'>

# equivalent methods exist for track, album, artist and playlists.
# a general search() method also exists, but check the api reference first!