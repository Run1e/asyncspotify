.. _ISO-3166-1: https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2

.. currentmodule:: asyncspotify

API Reference
*************

Client
======

The Spotify API wrapper client itself.

You can start a client in a context using the ``async with`` statement, see below. Do note the client calls
``Client.authenticate()`` itself, so you don't have to do this.

.. code-block:: py

	async with asyncspotify.Client(auth) as sp:
		# your code here

Otherwise, you would start a client like this:

.. code-block:: py

	sp = asyncspotify.Client(auth)
	await sp.authenticate()

	# your code here..

	# close the client session before you exit
	await sp.close()

.. autoclass:: Client
   :members:
   :special-members:
   :exclude-members: __weakref__

Spotify Objects
===============

.. note::

   None of these objects should be instantiated manually. They are returned by convenience methods in :class:`Client`.

.. autoclass:: SpotifyObject
   :members:

Track
-----

.. autoclass:: SimpleTrack
   :members:
   :inherited-members:

.. autoclass:: FullTrack
   :members:

.. autoclass:: PlaylistTrack
   :members:

Artist
------

.. autoclass:: SimpleArtist
   :members:
   :inherited-members:

.. autoclass:: FullArtist
   :members:

Playlist
--------

.. autoclass:: SimplePlaylist
   :members:
   :inherited-members:

.. autoclass:: FullPlaylist
   :members:

Album
-----

.. autoclass:: SimpleAlbum
   :members:
   :inherited-members:

.. autoclass:: FullAlbum
   :members:

Audio Features
--------------

.. autoclass:: AudioFeatures

Audio Analysis
--------------

.. autoclass:: AudioAnalysis

Image
-----

.. autoclass:: Image

User
----

.. autoclass:: PublicUser
   :members:
   :inherited-members:

.. autoclass:: PrivateUser
   :members:
   :inherited-members:

Playing Objects
---------------

.. autoclass:: CurrentlyPlaying
   :members:

.. autoclass:: CurrentlyPlayingContext
   :members:

Device
------

.. autoclass:: Device
   :members:

Authenticators
==============

A guide on how authentication works is located `here <https://developer.spotify.com/documentation/general/guides/authorization-guide/>`_.

Examples can also be found under the quickstart guide.

.. note::
   You do not have to worry about when your access token expires as the library will refresh the tokens automatically.
   Unless you're rolling your own authenticator, obviously.

ClientCredentialsFlow
---------------------

Only requires a client id and secret to authenticate. Does *not* give access to private resources. No refresh token
is used here. To extend, it simply authorizes again.

.. autoclass:: ClientCredentialsFlow
   :members:
   :inherited-members:

EasyAuthorizationCodeFlow
-------------------------

Extends :class:`AuthorizationCodeFlow` and requires one extra argument, ``storage``, which tells the authenticator which
file to store tokens in.

.. autoclass:: EasyAuthorizationCodeFlow
   :members:
   :inherited-members:

AuthorizationCodeFlow
---------------------

Exposes helper methods for implementing a version of the Authorization Code flow. :class:`EasyAuthorizationCodeFlow`
inherits from this and is recommended for most if access to private resources is required.

.. autoclass:: AuthorizationCodeFlow
   :members:
   :inherited-members:

Scope
=====

You can create a scope with specific permissions by passing kwargs in, like:

.. code-block:: py

   scope = Scope(
       user_top_read=True,
       playlist_modify_private=True
   )

.. autoclass:: Scope
   :members:
   :inherited-members:

   .. method:: all()

      Return :class:`Scope` with all scopes enabled.

   .. method:: none()

      Return :class:`Scope` with no scopes enabled.

Exceptions
==========

.. autoclass:: SpotifyException

.. autoclass:: HTTPException
   :show-inheritance:

.. autoclass:: BadRequest
   :show-inheritance:

.. autoclass:: Unauthorized
   :show-inheritance:

.. autoclass:: Forbidden
   :show-inheritance:

.. autoclass:: NotFound
   :show-inheritance:

.. autoclass:: NotAllowed
   :show-inheritance:

Utilities
=========

.. py:currentmodule:: asyncspotify.utils

.. autofunction:: get

.. autofunction:: find