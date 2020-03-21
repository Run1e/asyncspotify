import asyncio
import spoofy


async def main():
	# authenticate using the Client Credentials flow
	auth = spoofy.ClientCredentialsFlow(
		client_id='your client id',
		client_secret='your client secret',
	)
	
	# create and authorize your spotify client
	sp = spoofy.Client(auth)
	await sp.authorize()

	# done!
	playlist = await sp.get_playlist('1MG01HhbCvVhH9NmXhd9GC')
	for track in playlist.tracks:
		print(track.name)


asyncio.run(main())