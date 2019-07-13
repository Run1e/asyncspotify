# spoofy

![](https://readthedocs.org/projects/spoofy/badge/?version=latest)

spoofy is an asynchronous, object-oriented python wrapper for the Spotify Web API.

### Installation
Simply install it fro PyPi using pip!
```
pip install spoofy
```

### Documentation

The official documentation can be found on readthedocs: https://spoofy.readthedocs.io/

### Usage

The library provides easy to use authentication functions and intuitive method and hierarchies.

For complete examples, please check the documentation. Here's some snippets:

Creating an OAuth object and a Spotify Client:
```py
import spoofy

# create an authentication object, storing tokens in tokens.json
auth = await spoofy.easy_auth(
    client_id=client_id,
    client_secret=client_secret,
    scope=('playlist-modify-private', 'playlist-read-private'),
    cache_file='tokens.json'
)

sp = spoofy.Client(auth) # initialize a spotify client
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
