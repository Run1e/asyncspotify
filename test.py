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
	
	playlist = await sp.get_playlist('6WCb77q7WBfYbKT9VYst3R?si=gV6fUrI4RN2ixnfHkUeCAw')
	for index, track in enumerate(sorted(playlist.tracks, key=lambda t: t.popularity, reverse=True)):
		if index == 10:
			break
		print(f'{index+1}. {track.artists[0].name} - {track.name} ({track.popularity})')
	
	#track = await sp.get_track('')
	


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
