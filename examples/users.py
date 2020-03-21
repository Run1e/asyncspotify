# to get a user you can use the User getter:
user = await sp.get_user('user_id')
# <PublicUser id='user_id'>

# to get the user you're logged in as, use get_me:
me = await sp.get_me()
# <PrivateUser id='your_user_id'>

# user objects have methods themselves, such as create_playlist()
# check the api reference for a complete list!