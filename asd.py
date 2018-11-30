import asyncio, json, aiohttp
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
	
	session = aiohttp.ClientSession()
	
	# create an authentication object, storing tokens in tokens.json
	auth = await spoofy.easy_auth(
		client_id=client_id,
		client_secret=client_secret,
		scope=scope,
		session=session,
		cache_file='tokens.json'
	)
	
	# initialize a Client using the authentication object created above
	sp = spoofy.Client(
		auth=auth,
		session=session
	)
	
	me = await sp.get_me()
	
	tracks = await sp.get_album_tracks('7c2Xfq7aQKzs0KdSI3K7Rc')
	
	pprint(tracks)
	
	await session.close()
	
asyncio.run(main())

