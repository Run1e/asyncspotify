# this flow is "scoped", which means we have to list the resources we want access to.
# you can specify them like this, or do Scope.all() or Scope.none()
scope = asyncspotify.Scope(
	playlist_modify_public=True,
	playlist_modify_private=True,
	playlist_read_private=True,
	playlist_read_collaborative=True
)

# this is where our tokens will be stored
token_file = 'secret.json'

# create our authenticator
auth = asyncspotify.EasyAuthorizationCodeFlow(
	client_id='your client_id',
	client_secret='your client_secret',
	scope=scope,
	storage=token_file
)

# pass it to our new spotify client and authorize
sp = asyncspotify.Client(auth)
await sp.authorize()

# now we can do anything :)
print(await sp.get_me())