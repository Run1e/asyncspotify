# asyncspotify

![](https://readthedocs.org/projects/asyncspotify/badge/?version=latest)

asyncspotify is an asynchronous, object-oriented python wrapper for the Spotify Web API.

### Installation
Simply install it from PyPi using pip!
```
pip install asyncspotify
```

### Documentation

The official documentation can be found on readthedocs: https://asyncspotify.readthedocs.io/

### Usage

The library provides easy to use authentication functions and intuitive method and hierarchies.

To get going quickly, read the [quickstart](https://asyncspotify.readthedocs.io/en/latest/quickstart.html).

For complete examples, please check the documentation. Here's some snippets:

Authenticating using the Client Credentials flow, and getting a playlist:
```py
from asyncspotify import Client, ClientCredentialsFlow

auth = ClientCredentialsFlow(
    client_id='your client id',
    client_secret='your client secret',
)

async with Client(auth) as sp:
    playlist = await sp.get_playlist('1MG01HhbCvVhH9NmXhd9GC')
    for track in playlist.tracks:
        print(track.name)
```

Searching for and getting tracks:
```py
results = await sp.search_tracks(q='involvers', limit=2)
# [<SimpleTrack id='5xoJhWwvzPJD9k8j8BE2xO' name='27'>, <SimpleTrack id='0WUTBejxPUhURFCFfSYbDc' name='Fighting My Fight'>]

track = await sp.get_track('0hqAWKZDhuOfFb6aK002Ph')
# <FullTrack id='0hqAWKZDhuOfFb6aK002Ph' name='Bone Dry'>
```

Fetching and creating playlists:
```py
# get a playlist
playlist = await sp.get_playlist('1wPvaRtuI8mt10CpP2KnlO')
# <FullPlaylist id='1wPvaRtuI8mt10CpP2KnlO' name='my playlist'>

# iterate through playlist tracks
for track in playlist.tracks:
    print(track)

# get current user
me = await sp.get_me()
# <PrivateUser id='runie13'>

# create new playlist
my_playlist = await me.create_playlist(name='My playlist!')
# <FullPlaylist id='0YTCnj0WE5gGb1lRqD6Ks9' name='My playlist!'>

# add tracks from previews playlist to the new playlist
await my_playlist.add_tracks(*playlist.tracks)
```

### Reporting bugs

Please report issues [here on GitHub](https://github.com/Run1e/asyncspotify/issues).