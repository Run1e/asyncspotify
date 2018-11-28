import asyncio, json, aiohttp
from pprint import pprint

import spoofy

from config import *

async def main():
	session = aiohttp.ClientSession(loop=loop)
	
	scope = spoofy.Scope(
			'playlist-read-private',
			'playlist-modify-public',
			'playlist-modify-private',
			'playlist-read-private',
			'playlist-read-collaborative'
		)
	
	auther = spoofy.OAuth(
		session=session,
		client_id=client_id,
		client_secret=client_secret,
		redirect_uri=redirect_uri,
		scope=scope
	)
	
	await spoofy.easy_auth(auther, 'tokens.json')
	
	sp = spoofy.Client(
		auth=auther,
		session=session
	)
	
	await sp.get_me()
	
	#pl = await sp.user.create_playlist(name='ya boi', description='WHAT DU FAK')
	
	#for index, track in enumerate(sorted(playlist.tracks, key=lambda t: t.length, reverse=True)):
	#	print(f'{index+1}. {track.artists[0].name} - {track.name} ({track.length})')
	
	# get playlist
	playlist = await sp.get_playlist('0DwDTJVWRFsna3pKW03yqs')
	#pprint(playlist.tracks)
	print(playlist) # AutoHotkey
	print(playlist.owner)
	
	# get artists
	artist = await sp.get_artist('1gR0gsQYfi6joyO1dlp76N')
	print(artist) # Justice
	
	# get track
	track = await sp.get_track('19ts4uqOimLvSbu4DyOWE2')
	print(track) # Justice - Pleasure
	
	# get several tracks
	tracks = await sp.get_tracks('19ts4uqOimLvSbu4DyOWE2', '74ABBu8osxqmuFOAKcWWpG')
	pprint(tracks) # Pleasure, Forgiveness
	
	# get album
	album = await sp.get_album('1c9Sx7XdXuMptGyfCB6hHs')
	print(album) # After Laughter
	pprint(album.artists) # Paramore
	pprint(album.tracks) # 12 songs
	
	# get several albums
	albums = await sp.get_albums('1c9Sx7XdXuMptGyfCB6hHs', '1bt6q2SruMsBtcerNVtpZB')
	pprint(albums)
	
	await session.close()
	
loop = asyncio.get_event_loop()
loop.run_until_complete(main())