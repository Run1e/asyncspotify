# specify your scope. you can also do Scope.all() or Scope.none()
scope = asyncspotify.Scope(
	playlist_modify_public=True,
	playlist_modify_private=True,
	playlist_read_private=True,
	playlist_read_collaborative=True
)

# your tokens are stored here
token_file = 'tokens.json'

auth = asyncspotify.EasyCodeFlow(
	client_id='your client_id',
	client_secret='your client_secret',
	scope=scope,
	store=token_file
)

sp = asyncspotify.Client(auth)
await sp.authorize()

print(await sp.get_me())