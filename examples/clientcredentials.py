import asyncio
import asyncspotify


async def main():
	# authenticate using the Client Credentials flow
	auth = asyncspotify.ClientCredentialsFlow(
		client_id='your client id',
		client_secret='your client secret',
	)
	
	# create and authorize your spotify client
	sp = asyncspotify.Client(auth)
	await sp.authorize()

	# done!
	playlist = await sp.get_playlist('1MG01HhbCvVhH9NmXhd9GC')
	async for track in playlist:
		print(track.name)


asyncio.run(main())