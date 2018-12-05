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
	sp = spoofy.Client(auth)
	
	pprint(await sp.search_album('choose your weapon'))
	
	await auth.session.close()
	
asyncio.run(main())

