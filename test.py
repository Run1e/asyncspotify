import asyncio, json, aiohttp
from pprint import pprint

import spoofy

from config import *

async def main():
	session = aiohttp.ClientSession(loop=loop)
	
	auther = spoofy.OAuth(
		session=session,
		client_id=client_id,
		client_secret=client_secret,
		redirect_uri=redirect_uri,
		scope=scope
	)
	
	await spoofy.auto_auth(auther, 'tokens.json')
	
	sp = spoofy.Client(
		auth=auther,
		session=session
	)
	#for index, track in enumerate(sorted(playlist.tracks, key=lambda t: t.length, reverse=True)):
	#	print(f'{index+1}. {track.artists[0].name} - {track.name} ({track.length})')
	
	playlist = await sp.get_playlist('1x96mtM5csCrplJqQcfiBp')
	
	artist = await sp.get_artist('1gR0gsQYfi6joyO1dlp76N')
	track = await sp.get_track('19ts4uqOimLvSbu4DyOWE2')
	tracks = await sp.get_tracks('19ts4uqOimLvSbu4DyOWE2', '74ABBu8osxqmuFOAKcWWpG')
	album = await sp.get_album('1c9Sx7XdXuMptGyfCB6hHs')
	
	print(playlist) # AutoHotkey
	print(artist) # Justice
	print(track) # Justice - Pleasure
	pprint(tracks) # Pleasure, Forgiveness
	print(album) # After Laughter
	pprint(album.images) # three images
	pprint(album.artists) # Paramore
	pprint(album.tracks) # 12 songs
	pprint(playlist.tracks)
	
	await playlist.add_tracks(*album.tracks)
	
	await session.close()
	
loop = asyncio.get_event_loop()
loop.run_until_complete(main())