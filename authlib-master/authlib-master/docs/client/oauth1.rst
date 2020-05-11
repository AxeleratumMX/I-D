OAuth 1 Client
==============

.. meta::
    :description: An OAuth 1 protocol implementation for requests.Session
        powered by Authlib.

.. module:: authlib.client


OAuth1Session for requests
--------------------------

The :class:`OAuth1Session` in Authlib is a subclass of ``requests.Session``.
It shares the same API with ``requests.Session`` and extends it with OAuth 1
protocol. This section is a guide on how to obtain an access token in OAuth 1
flow.

.. note::
    If you are using Flask or Django, you may have interests in
    :ref:`flask_client` and :ref:`django_client`.

If you are not familiar with OAuth 1.0, it is better to
:ref:`understand_oauth1` now.

There are three steps in OAuth 1 to obtain an access token. Initialize
the session for reuse::

    >>> from authlib.client import OAuth1Session
    >>> client_id = 'Your Twitter client key'
    >>> client_secret = 'Your Twitter client secret'
    >>> session = OAuth1Session(client_id, client_secret)

.. _fetch_request_token:

Fetch Temporary Credential
~~~~~~~~~~~~~~~~~~~~~~~~~~

The first step is to fetch temporary credential, which will be used to generate
authorization URL::

    >>> request_token_url = 'https://api.twitter.com/oauth/request_token'
    >>> request_token = session.fetch_request_token(request_token_url)
    >>> print(request_token)
    {'oauth_token': 'gA..H', 'oauth_token_secret': 'lp..X', 'oauth_callback_confirmed': 'true'}

Save this temporary credential for later use (if required).

You can assign a ``redirect_uri`` before fetching the request token, if
you want to redirect back to another URL other than the one you registered::

    >>> session.redirect_uri = 'https://your-domain.org/auth'
    >>> session.fetch_request_token(request_token_url)

Redirect to Authorization Endpoint
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The second step is to generate the authorization URL::

    >>> authenticate_url = 'https://api.twitter.com/oauth/authenticate'
    >>> session.create_authorization_url(authenticate_url, request_token['oauth_token'])
    'https://api.twitter.com/oauth/authenticate?oauth_token=gA..H'

Actually, the second parameter ``request_token`` can be omitted, since session
is re-used::

    >>> session.create_authorization_url(authenticate_url)

Now visit the authorization url that :meth:`OAuth1Session.create_authorization_url`
generated, and grant the authorization.

.. _fetch_oauth1_access_token:

Fetch Access Token
~~~~~~~~~~~~~~~~~~

When the authorization is granted, you will be redirected back to your
registered callback URI. For instance::

    https://example.com/twitter?oauth_token=gA..H&oauth_verifier=fcg..1Dq

If you assigned ``redirect_uri`` in :ref:`fetch_oauth1_access_token`, the
authorize response would be something like::

    https://your-domain.org/auth?oauth_token=gA..H&oauth_verifier=fcg..1Dq

Now fetch the access token with this response::

    >>> resp_url = 'https://example.com/twitter?oauth_token=gA..H&oauth_verifier=fcg..1Dq'
    >>> session.parse_authorization_response(resp_url)
    >>> access_token_url = 'https://api.twitter.com/oauth/access_token'
    >>> token = session.fetch_access_token(access_token_url)
    >>> print(token)
    {
        'oauth_token': '12345-st..E',
        'oauth_token_secret': 'o67..X',
        'user_id': '12345',
        'screen_name': 'lepture',
        'x_auth_expires': '0'
    }
    >>> save_access_token(token)

Save this token to access protected resources.

The above flow is not always what we will use in a real project. When we are
redirected to authorization endpoint, our session is over. In this case, when
the authorization server send us back to our server, we need to create another
session::

    >>> # restore your saved request token, which is a dict
    >>> request_token = restore_request_token()
    >>> oauth_token = request_token['oauth_token']
    >>> oauth_token_secret = request_token['oauth_token_secret']
    >>> session = OAuth1Session(
    ...     client_id, client_secret,
    ...     token=oauth_token,
    ...     token_secret=oauth_token_secret)
    >>> # there is no need for `parse_authorization_response` if you can get `verifier`
    >>> verifier = request.args.get('verifier')
    >>> access_token_url = 'https://api.twitter.com/oauth/access_token'
    >>> token = session.fetch_access_token(access_token_url, verifier)

Access Protected Resources
~~~~~~~~~~~~~~~~~~~~~~~~~~

Now you can access the protected resources. If you re-use the session, you
don't need to do anything::

    >>> account_url = 'https://api.twitter.com/1.1/account/verify_credentials.json'
    >>> resp = session.get(account_url)
    <Response [200]>
    >>> resp.json()
    {...}

The above is not the real flow, just like what we did in
:ref:`fetch_oauth1_access_token`, we need to create another session ourselves::

    >>> access_token = restore_access_token_from_database()
    >>> oauth_token = access_token['oauth_token']
    >>> oauth_token_secret = access_token['oauth_token_secret']
    >>> session = OAuth1Session(
    ...     client_id, client_secret,
    ...     token=oauth_token,
    ...     token_secret=oauth_token_secret)
    >>> account_url = 'https://api.twitter.com/1.1/account/verify_credentials.json'
    >>> resp = session.get(account_url)

Please note, there are duplicated steps in the documentation, read carefully
and ignore the duplicated explains.

Using OAuth1Auth
~~~~~~~~~~~~~~~~

It is also possible to access protected resources with ``OAuth1Auth`` object.
Create an instance of OAuth1Auth with an access token::

    auth = OAuth1Auth(
        client_id='..',
        client_secret=client_secret='..',
        token='oauth_token value',
        token_secret='oauth_token_secret value',
        ...
    )

Pass this ``auth`` to ``requests` to access protected resources::

    import requests

    url = 'https://api.twitter.com/1.1/account/verify_credentials.json'
    resp = requests.get(url, auth=auth)
