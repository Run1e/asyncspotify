Examples
********

Here are some various examples on how to misc. operations.

Authenticating
==============

.. literalinclude:: ../examples/authenticating.py
    :language: python

Getting Spotify Objects
=======================

.. code-block:: py

    track = await sp.get_track('track_id')
    # <FullTrack id='track_id' name='track name here'>

    album = await sp.get_artist('artist_id')
    # <FullArtist id='artist_id' name='artist name here'>

    # and so on for playlists and albums...

    # to get several instances:

    albums = await sp.get_albums('album_id_1', 'album_id_2')
    # [<FullAlbum id='album_id_1' ...>, <FullAlbum id='album_id_2' ...>]

Getting playlists and adding tracks
===================================

.. code-block:: py

    # get a playlist
    playlist = await sp.get_playlist('1wPvaRtuI8mt10CpP2KnlO')

    # iterate tracks
    for track in playlist.tracks:
        print(track)

    # get the user we're logged in as
    me = await sp.get_me()
    # <PrivateUser id='runie13'>

    # create a playlist
    my_playlist = await me.create_playlist(name='My playlist!', description='This is the playlist description.')
    # <FullPlaylist id='0FECu9cwvviV3rwOjDqU9j' name='My playlist!'>

    # add tracks from the first playlist to newly created second playlist
    await my_playlist.add_tracks(*playlist.tracks)

Searching
=========

.. code-block:: py

    # get multiple tracks from one query
    tracks = await sp.search_tracks(q='involvers', limit=2)
    # [<SimpleTrack id='5xoJhWwvzPJD9k8j8BE2xO' name='27'>, <SimpleTrack id='0WUTBejxPUhURFCFfSYbDc' name='Fighting My Fight'>]

    album = await sp.search_album('hiatus kaiyote')
    # <SimpleAlbum id='3qzmmmRmVBiOuMvrerfW4z' name='Choose Your Weapon'>

    # equivalent methods exist for track, album, artist and playlists.
    # a general search() method also exists, but check the api reference first!

Getting users/yourself
======================

.. code-block:: py

    # to get a user you can use the User getter:
    user = await sp.get_user('user_id')
    # <PublicUser id='user_id'>

    # to get the user you're logged in as, use get_me:
    me = await sp.get_me()
    # <PrivateUser id='your_user_id'>

    # user objects have methods themselves, such as create_playlist()
    # check the api reference for a complete list!