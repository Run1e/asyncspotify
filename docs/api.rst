.. currentmodule:: spoofy

API Reference
*************

Client
======

.. autoclass:: Client
    :members:
    :special-members:
    :exclude-members: __weakref__

Spotify Objects
===============

.. note::
    None of these objects should be instantiated manually. They are returned by convenience methods in :class:`Client`.

.. autoclass:: Object
    :members:

Track
-----

.. autoclass:: Track
    :members:

.. autoclass:: SimpleTrack
    :members:

.. autoclass:: FullTrack
    :members:

.. autoclass:: PlaylistTrack
    :members:

Artist
------

.. autoclass:: Artist
    :members:

.. autoclass:: SimpleArtist
    :members:

.. autoclass:: FullArtist
    :members:

Playlist
--------

.. autoclass:: Playlist
    :members:

.. autoclass:: SimplePlaylist
    :members:

.. autoclass:: FullPlaylist
    :members:

Album
-----

.. autoclass:: Album
    :members:

.. autoclass:: SimpleAlbum
    :members:

.. autoclass:: FullAlbum
    :members:

User
----

.. autoclass:: User
    :members:

.. autoclass:: PublicUser
    :members:

.. autoclass:: PrivateUser
    :members:

OAuth
=====

.. autoclass:: OAuth
    :members:

.. autocofunction:: easy_auth

Exceptions
==========

.. py:currentmodule:: spoofy.exceptions

.. autoclass:: SpoofyException

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

.. py:currentmodule:: spoofy.utils

.. autofunction:: get

.. autofunction:: find