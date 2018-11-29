# spoofy

spoofy is an asynchronous, object-oriented python wrapper for the Spotify Web API.

### Usage

The library provides easy to use authentication functions and intuitive method and hierarchies.

```py
import asyncio
import spoofy

async def main():
	# create an authentication object, storing tokens in tokens.json
	auth = await spoofy.easy_auth(
		client_id=client_id,
		client_secret=client_secret,
		scope=('playlist-modify-private', 'playlist-read-private'),
		cache_file='tokens.json'
	)
	
	# initialize a Client using the authentication object created above
	sp = spoofy.Client(auth)
	
	# search for 5 tracks using query 'powerwolf'
	results = await sp.search_tracks(q='powerwolf', total=5)
	
	# iterate tracks
	for track in results:
		print(track)
	
	# get a track
	track = await sp.get_track('0hqAWKZDhuOfFb6aK002Ph')
	
	# get a playlist
	playlist = await sp.get_playlist('1wPvaRtuI8mt10CpP2KnlO')
	
	# iterate through playlist tracks
	for track in playlist.tracks:
		print(track)
	
	# get current user
	me = await sp.get_me()
	
	# create new playlist
	new_playlist = await me.create_playlist(name='My playlist!')
	
	# add tracks from previews playlist to the new playlist
	await new_playlist.add_tracks(*playlist.tracks)
	
loop = asyncio.get_event_loop()
loop.run_until_complete(main())
```

### Installation
Simply install it via pip!
```
pip install spoofy
```