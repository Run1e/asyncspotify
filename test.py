import asyncio, json, aiohttp

import spoofy

from config import *

async def main():
	session = aiohttp.ClientSession(loop=loop)
	
	auther = spoofy.OAuth(
		session = session,
		client_id=client_id,
		client_secret=client_secret,
		redirect_uri=redirect_uri,
		scope=scope
	)
	
	data = json.loads(open('tokens.json', 'r').read())
	
	auther.access_token = data['access_token']
	auther.refresh_token = data['refresh_token']
	
	sp = spoofy.Client(
		auth=auther,
		session=session
	)
	
	playlist = await sp.get_playlist('0DwDTJVWRFsna3pKW03yqs?si=l_jgKkcVTdWemz3V-_g_9Q')
	print(playlist)
	


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
