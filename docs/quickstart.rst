.. py:currentmodule:: asyncspotify

Quickstart
**********

This page will guide into installing and setting up a client.

Installing
==========

The recommended way of installing this library is from PyPI.

.. code-block:: py

    pip install asyncspotify

Run pip as a module to install for a specific version of Python:

.. code-block:: py

    python3.7 -m pip install asyncspotify

To test your installation, you can import ``asyncspotify`` and print the version string:

.. code-block:: py

    import asyncspotify
    print(asyncspotify.__version__)

Getting started
===============

To communicate with the Spotify Web API, you have to create a Spotify Application first.
Go to `this page <https://developer.spotify.com/dashboard/applications>`_ and create an app.

After having made an app, you will be forwarded to a page showing miscellaneous stats. The client id and client secret
provided here is what you'll use when authenticating. If you're going to use the :class:`EasyAuthenticationCodeFlow` authorizer,
you have to click edit and add ``http://localhost/`` to the list of redirect URIs.

To authenticate, you have to create an authenticator. If you do *not* need to access or modify personal data, you can
simply use the :class:`ClientCredentialsFlow` class:

.. literalinclude:: ../examples/clientcredentials.py
    :language: py

If you *do* need to access and modify personal data, you will have to use the Authentication Code flow and specify
the *scope* you require. The easiest way to do this is to use the :class:`EasyAuthenticationCodeFlow` class, which will handle
storing your tokens and fetching them when your program restarts:

.. literalinclude:: ../examples/easyauthorizationcodeflow.py
    :language: py

The :class:`EasyAuthenticationCodeFlow` requires a first-time setup, please follow the steps in your console carefully.
Remember to add ``http://localhost/`` to the list of redirect URIs on your Spotify Application page!

If you need more granular control of how tokens are stored, you can extend :class:`AuthenticationCodeFlow` with your
own methods.

To see some basic usage of the API, see the examples. For everything else, see the API Reference.