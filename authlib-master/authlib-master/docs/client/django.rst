.. _django_client:

Django OAuth Client
===================

.. meta::
    :description: The built-in Django integrations for OAuth 1.0 and
        OAuth 2.0 clients.

.. module:: authlib.django.client

Looking for OAuth providers?

- :ref:`django_oauth1_server`
- OAuth 2 provider is not ready

The Django client shares a similar API with Flask client. But there are
differences, since Django has no request context, you need to pass ``request``
argument yourself.

Create a registry with :class:`OAuth` object::

    from authlib.django.client import OAuth

    oauth = OAuth()

Configuration
-------------

To register a remote application on OAuth registry, using the
:meth:`~OAuth.register` method::

    oauth.register(
        'twitter',
        client_id='Twitter Consumer Key',
        client_secret='Twitter Consumer Secret',
        request_token_url='https://api.twitter.com/oauth/request_token',
        request_token_params=None,
        access_token_url='https://api.twitter.com/oauth/access_token',
        access_token_params=None,
        refresh_token_url=None,
        authorize_url='https://api.twitter.com/oauth/authenticate',
        api_base_url='https://api.twitter.com/1.1/',
        client_kwargs=None,
    )

The first parameter in ``register`` method is the **name** of the remote
application. You can access the remote application with::

    oauth.twitter.get('account/verify_credentials.json')

The second parameter in ``register`` method is configuration. Every key value
pair can be omit. They can be configured from your Django settings::

    AUTHLIB_OAUTH_CLIENTS = {
        'twitter': {
            'client_id': 'Twitter Consumer Key',
            'client_secret': 'Twitter Consumer Secret',
            'request_token_url': 'https://api.twitter.com/oauth/request_token',
            'request_token_params': None,
            'access_token_url': 'https://api.twitter.com/oauth/access_token',
            'access_token_params': None,
            'refresh_token_url': None,
            'authorize_url': 'https://api.twitter.com/oauth/authenticate',
            'api_base_url': 'https://api.twitter.com/1.1/',
            'client_kwargs': None
        }
    }

client_kwargs
~~~~~~~~~~~~~

The ``client_kwargs`` is a dict configuration to pass extra parameters to
``OAuth1Session`` or ``OAuth2Session``.

For OAuth 1.0, you can pass extra parameters like::

    client_kwargs = {
        'signature_method': 'HMAC-SHA1',
        'signature_type': 'HEADER',
        'rsa_key': 'Your-RSA-Key'
    }

For OAuth 2.0, you can pass extra parameters like::

    client_kwargs = {
        'scope': 'profile',
        'token_endpoint_auth_method': 'client_secret_basic',
        'token_placement': 'header',
    }

There are several ``token_endpoint_auth_method``, get a deep inside the
:ref:`client_auth_methods`.

Sessions Middleware
-------------------

In OAuth 1, Django client will save the request token in sessions. In this
case, you need to configure Session Middleware in Django::

    MIDDLEWARE = [
        'django.contrib.sessions.middleware.SessionMiddleware'
    ]

Follow the official Django documentation to set a proper session. Either a
database backend or a cache backend would work well.

.. warning::

    Be aware, using secure cookie as session backend will expose your request
    token.


Database Design
---------------

Authlib Django client has no built-in database model. You need to design the
Token model by yourself. This is designed by intention.

Here are some hints on how to design your schema::

    class OAuth1Token(models.Model):
        name = models.CharField(max_length=40)
        oauth_token = models.CharField(max_length=200)
        oauth_token_secret = models.CharField(max_length=200)
        # ...

        def to_token(self):
            return dict(
                oauth_token=self.access_token,
                oauth_token_secret=self.alt_token,
            )

    class OAuth2Token(models.Model):
        name = models.CharField(max_length=40)
        token_type = models.CharField(max_length=20)
        access_token = models.CharField(max_length=200)
        refresh_token = models.CharField(max_length=200)
        # oauth 2 expires time
        expires_at = models.DateTimeField()
        # ...

        def to_token(self):
            return dict(
                access_token=self.access_token,
                token_type=self.token_type,
                refresh_token=self.refresh_token,
                expires_at=self.expires_at,
            )


Implement the Server
--------------------

There are two views to be completed, no matter it is OAuth 1 or OAuth 2::

    def login(request):
        # build a full authorize callback uri
        redirect_uri = request.build_absolute_uri('/authorize')
        return oauth.twitter.authorize_redirect(request, redirect_uri)

    def authorize(request):
        token = oauth.twitter.authorize_access_token(request)
        # save_token_to_db(token)
        return '...'

    def fetch_resource(request):
        token = get_user_token_from_db(request.user)
        # remember to assign user's token to the client
        resp = oauth.twitter.get('account/verify_credentials.json', token=token)
        profile = resp.json()
        # ...

.. versionadded:: v0.10

When using the oauth client to make HTTP requests, developers will always need
to get the ``token`` and pass the ``token`` into the requests. Here is an improved
way to handle this issue with ``fetch_token`` feature::

    def fetch_twitter_token(request):
        item = OAuth1Token.objects.get(
            name='twitter',
            user=request.user
        )
        return item.to_token()

    # we can registry this ``fetch_token`` with oauth.register
    oauth.register(
        'twitter',
        client_id='Twitter Consumer Key',
        client_secret='Twitter Consumer Secret',
        request_token_url='https://api.twitter.com/oauth/request_token',
        request_token_params=None,
        access_token_url='https://api.twitter.com/oauth/access_token',
        access_token_params=None,
        refresh_token_url=None,
        authorize_url='https://api.twitter.com/oauth/authenticate',
        api_base_url='https://api.twitter.com/1.1/',
        client_kwargs=None,
        # NOTICE HERE
        fetch_token=fetch_twitter_token,
    )

Developers can also pass the ``fetch_token`` to ``OAuth`` registry so that
they don't have to pass a ``fetch_token`` for each remote app. In this case,
the ``fetch_token`` will accept two parameters::

    def fetch_token(name, request):
        if name in OAUTH1_SERVICES:
            model = OAuth1Token
        else:
            model = OAuth2Token

        item = model.objects.get(
            name=name,
            user=request.user
        )
        return item.to_token()

    oauth = OAuth(fetch_token=fetch_token)

Now, developers don't have to pass a ``token`` in the HTTP requests,
instead, they can pass the ``request``::

    def fetch_resource(request):
        resp = oauth.twitter.get('account/verify_credentials.json', request=request)
        profile = resp.json()
        # ...

Code Challenge
--------------

Adding ``code_challenge`` provided by :ref:`specs/rfc7636` is simple. You
register your remote app with a ``code_challenge_method``::

    oauth.register(
        'example',
        client_id='Example Client ID',
        client_secret='Example Client Secret',
        access_token_url='https://example.com/oauth/access_token',
        authorize_url='https://example.com/oauth/authorize',
        api_base_url='https://api.example.com/',
        client_kwargs=None,
        code_challenge_method='S256',
    )

Note, the only supportted ``code_challenge_method`` is ``S256``.

Compliance Fix
--------------

The :class:`RemoteApp` is a subclass of :class:`~authlib.client.OAuthClient`,
they share the same logic for compliance fix. Construct a method to fix
requests session::

    def slack_compliance_fix(session):
        def _fix(resp):
            token = resp.json()
            # slack returns no token_type
            token['token_type'] = 'Bearer'
            resp._content = to_unicode(json.dumps(token)).encode('utf-8')
            return resp
        session.register_compliance_hook('access_token_response', _fix)

When :meth:`OAuth.register` a remote app, pass it in the parameters::

    oauth.register(
        'slack',
        client_id='...',
        client_secret='...',
        ...,
        compliance_fix=slack_compliance_fix,
        ...
    )

Find all the available compliance hooks at :ref:`compliance_fix_oauth2`.


Loginpass
---------

There are many built-in integrations served by loginpass_, checkout the
``django_example`` in loginpass project. Here is an example of GitHub::

    from authlib.django.client import OAuth
    from loginpass import create_django_urlpatterns, GitHub

    oauth = OAuth()

    def handle_authorize(request, remote, token, user_info):
        if token:
            save_token(request, remote.name, token)
        if user_info:
            save_user(request, user_info)
            return user_page
        raise some_error

    oauth_urls = create_django_urlpatterns(GitHub, oauth, handle_authorize)


    # Register it in ``urls.py``
    from django.urls import include, path

    urlpatterns = [...]
    urlpatterns.append(path('/github/', include(oauth_urls)))
    # Now, there are: ``/github/login`` and ``/github/auth``

The source code of loginpass is very simple, they are just preconfigured
services integrations.

.. _loginpass: https://github.com/authlib/loginpass
