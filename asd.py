import asyncio
from pprint import pprint

import spoofy

from config import *

async def main():
	scope = (
		'user-top-read',
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
	
	await auth.refresh()
	
	# initialize a Client using the authentication object created above
	sp = spoofy.Client(auth=auth)
	
	tracks = await sp.get_playlist_tracks('1wPvaRtuI8mt10CpP2KnlO')
	
	for track in tracks:
		pprint(track.name)
		
	
	await auth.session.close()
	
asyncio.run(main())

