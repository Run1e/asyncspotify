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
provided here is what you'll use when authenticating.

To authenticate, you have to create an :class:`OAuth` instance. The easiest way of doing this is calling the
convenience function :func:`easy_auth`. The following snippet shows how to authenticate and use the returned
instance to create a Spoofy Client instance.

.. literalinclude:: ../examples/authenticating.py
    :language: py

To make :func:`easy_auth` work, you have to go to the dashboard of your application, click edit, and add this
to your list of 'redirect URIs': ``http://localhost/``

The first time you authenticate, a link and some instructions will appear in your console. The link points to a page
where you can grant yourself access. After granting access your browser will be redirected to a page (localhost if
you're using :func:`easy_auth`). The redirect URL contains a code needed to continue. Copy the URL and paste it into
your console and press enter (sometimes pressing enter twice is needed). After this you're finished authenticating!

To see some basic usage of the API, see the examples. For everything else, see the API Reference.