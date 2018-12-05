import spoofy
import asyncio


async def main():
	
	# define the scopes you need
	scope = (
		'playlist-modify-public',
		'playlist-modify-private',
		'playlist-read-private',
		'playlist-read-collaborative'
	)
	
	# create auth instance
	auth = await spoofy.easy_auth(
		client_id='your client_id',
		client_secret='your client_secret',
		scope=scope,
		cache_file='tokens.json'
	)
	
	# create spotify client
	sp = spoofy.Client(auth)


	# at this point you can do whatever you want with the
	# client object (within the scopes you defined).
	# all the following examples are assumed to have
	# have a client instance initialized called sp


asyncio.run(main())