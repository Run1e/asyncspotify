import asyncio, json, aiohttp
from pprint import pprint

import spoofy

from config import *

async def main():
	scope = (
		'playlist-modify-public',
		'playlist-modify-private',
		'playlist-read-private',
		'playlist-read-collaborative'
	)
	
	# create an authentication object, storing tokens in tokens.json
	auth = await spoofy.easy_auth(
		client_id=client_id,
		client_secret=client_secret,
		scope=scope,
		cache_file='tokens.json'
	)
	
	# initialize a Client using the authentication object created above
	sp = spoofy.Client(auth)
	
	# search for 5 tracks using query 'powerwolf'
	results = await sp.search_tracks(q='involvers', total=2)
	print(results)
	
	# get a track
	track = await sp.get_track('0hqAWKZDhuOfFb6aK002Ph')
	print(repr(track))
	
	# get a playlist
	playlist = await sp.get_playlist('1wPvaRtuI8mt10CpP2KnlO')
	print(repr(playlist))
	
	# iterate through playlist tracks
	for track in playlist.tracks:
		pass
		#print(track)
	
	# get current user
	me = await sp.get_me()
	print(me)
	
	# create new playlist
	new_playlist = await me.create_playlist(name='My playlist!')
	print(repr(new_playlist))
	
	# add tracks from previews playlist to the new playlist
	await new_playlist.add_tracks(*playlist.tracks)
	
loop = asyncio.get_event_loop()
loop.run_until_complete(main())

