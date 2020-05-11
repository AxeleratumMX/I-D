.. _flask_oauth1_server:

Flask OAuth 1.0 Server
======================

.. meta::
    :description: How to create an OAuth 1.0 server in Flask with Authlib.
        And understand how OAuth 1.0 works.

Implement OAuth 1.0 provider in Flask. An OAuth 1 provider contains two servers:

- Authorization Server: to issue access tokens
- Resources Server: to serve your users' resources

At the very beginning, we need to have some basic understanding of
:ref:`the OAuth 1.0 <understand_oauth1>`.

.. important::

    If you are developing on your localhost, remember to set the environment
    variable::

        export AUTHLIB_INSECURE_TRANSPORT=true

Here are the details in documentation:

.. toctree::
    :maxdepth: 2

    authorization-server
    resource-server
    customize
    api
