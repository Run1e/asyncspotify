import asyncio, json

import spoofy

from config import *

async def main():
	"""
	oauth = spoofy.OAuth(
		client_id=client_id
		client_secret=client_secret,
		redirect_uri=redirect_uri,
		scope=scope,
		loop=loop
	)
	
	access_token, refresh_token, expires_in = await oauth.authorize()
	
	with open('tokens.json', 'w') as f:
		f.write(json.dumps({'access_token': access_token, 'refresh_token': refresh_token}))
	
	"""
	
	data = json.loads(open('tokens.json', 'r').read())
	
	sp = spoofy.Client(
		data['access_token'],
		data['refresh_token']
	)
	
	playlist = await sp.get_playlist('0DwDTJVWRFsna3pKW03yqs?si=l_jgKkcVTdWemz3V-_g_9Q')
	
	print(playlist)
	


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
