.. py:currentmodule:: spoofy

Quickstart
**********

This page will guide into installing and setting up a client.

Installing
==========

The recommended way of installing this library is from PyPi.

.. code-block:: py

    pip install spoofy

If you're installing for a specific python version, do:

.. code-block:: py

    python3.7 -m pip install spoofy

Upon installation, the following code should show the version number of the lib:

.. code-block:: py

    import spoofy

    print(spoofy.__version__)

Getting started
===============

To communicate with the Spotify Web API, you have to create a Spotify Application first.
Go to `this page <https://developer.spotify.com/dashboard/applications>`_ and create an app.

After having made an app, you will be forwarded to a page showing miscellaneous stats. The client id and client secret
provided here is what you'll use when authenticating. If you're going to use the :class:`EasyCodeFlow` authorizer,
you have to click edit and add ``http://localhost/`` to the list of redirect URIs.

To authenticate, you have to create an authenticator. If you do *not* need to access or modify personal data, you can
simply use the :class:`ClientCredentialsFlow` class:

.. literalinclude:: ../examples/clientcredentials.py
    :language: py

If you *do* need to access and modify personal data, you will have to use the Authentication Code flow and specify
the *scope* you require. The easiest way to do this is to use the :class:`EasyCodeFlow` class, which will handle
storing your tokens and fetching them when your program restarts:

.. literalinclude:: ../examples/easycodeflow.py
    :language: py

The :class:`EasyCodeFlow` requires a first-time setup, please follow the steps in your console carefully.
Remember to add ``http://localhost/`` to the list of redirect URIs on your Spotify Application page!

To see some basic usage of the API, see the examples. For everything else, see the API Reference.