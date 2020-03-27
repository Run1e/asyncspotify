asyncspotify
============

.. image:: https://img.shields.io/pypi/v/asyncspotify.svg
   :target: https://python.pypi.org/project/asyncspotify/
   :alt: PyPI version info

.. image:: https://readthedocs.org/projects/asyncspotify/badge/?version=latest
   :target: https://asyncspotify.readthedocs.io/en/latest/
   :alt: RTD Documentation

asyncspotify is an asynchronous, object-oriented python wrapper for the Spotify Web API.

Installation
------------

Simply install the library from PyPI:

.. code:: sh

   python -m pip install asyncspotify

Documentation
-------------

The documentation can be found at `readthedocs <https://asyncspotify.readthedocs.io/>`_.

Usage
-----

To get going quickly, read the `quickstart <https://asyncspotify.readthedocs.io/en/latest/quickstart.html>`_.

For complete examples, please check the documentation. Here's some snippets:


Authenticating using the Client Credentials flow, and getting a playlist:

.. code:: py

   from asyncspotify import Client, ClientCredentialsFlow

   auth = ClientCredentialsFlow(
      client_id='your client id',
      client_secret='your client secret',
   )

   async with Client(auth) as sp:
      playlist = await sp.get_playlist('1MG01HhbCvVhH9NmXhd9GC')
      for track in playlist.tracks:
         print(track.name)

Searching for and getting tracks:

.. code:: py

   results = await sp.search_tracks(q='involvers', limit=2)
   # [<SimpleTrack id='5xoJhWwvzPJD9k8j8BE2xO' name='27'>, <SimpleTrack id='0WUTBejxPUhURFCFfSYbDc' name='Fighting My Fight'>]

   track = await sp.get_track('0hqAWKZDhuOfFb6aK002Ph')
   # <FullTrack id='0hqAWKZDhuOfFb6aK002Ph' name='Bone Dry'>

Fetching and creating playlists:

.. code:: py

   # get a playlist
   playlist = await sp.get_playlist('1wPvaRtuI8mt10CpP2KnlO')
   # <FullPlaylist id='1wPvaRtuI8mt10CpP2KnlO' name='my playlist'>

   # iterate through playlist tracks
   for track in playlist.tracks:
      print(track)

   # get current user
   me = await sp.get_me()
   # <PrivateUser id='runie13'>

   # create new playlist
   my_playlist = await me.create_playlist(name='My playlist!')
   # <FullPlaylist id='0YTCnj0WE5gGb1lRqD6Ks9' name='My playlist!'>

   # add tracks from previews playlist to the new playlist
   await my_playlist.add_tracks(*playlist.tracks)

Reporting bugs
--------------

Please report issues here at `GitHub <https://github.com/Run1e/asyncspotify/issues>`_.