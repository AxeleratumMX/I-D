from flask import json
from authlib.common.urls import urlparse, url_decode
from authlib.flask.oauth2 import register_cache_authorization_code
from authlib.oauth2.rfc6749.grants import (
    AuthorizationCodeGrant as _AuthorizationCodeGrant,
)
from .models import db, User, Client, AuthorizationCode
from .models import CodeGrantMixin, generate_authorization_code
from .oauth2_server import TestCase
from .oauth2_server import create_authorization_server
from ..cache import SimpleCache


class AuthorizationCodeGrant(CodeGrantMixin, _AuthorizationCodeGrant):
    def create_authorization_code(self, client, grant_user, request):
        return generate_authorization_code(client, grant_user, request)


class AuthorizationCodeTest(TestCase):
    LAZY_INIT = False

    def register_grant(self, server):
        server.register_grant(AuthorizationCodeGrant)

    def prepare_data(
            self, is_confidential=True,
            response_type='code', grant_type='authorization_code',
            token_endpoint_auth_method='client_secret_basic'):
        server = create_authorization_server(self.app, self.LAZY_INIT)
        self.register_grant(server)
        self.server = server

        user = User(username='foo')
        db.session.add(user)
        db.session.commit()

        if is_confidential:
            client_secret = 'code-secret'
        else:
            client_secret = ''
        client = Client(
            user_id=user.id,
            client_id='code-client',
            client_secret=client_secret,
            redirect_uri='https://a.b',
            scope='profile address',
            token_endpoint_auth_method=token_endpoint_auth_method,
            response_type=response_type,
            grant_type=grant_type,
        )
        self.authorize_url = (
            '/oauth/authorize?response_type=code'
            '&client_id=code-client'
        )
        db.session.add(client)
        db.session.commit()

    def test_get_authorize(self):
        self.prepare_data()
        rv = self.client.get(self.authorize_url)
        self.assertEqual(rv.data, b'ok')

    def test_invalid_client_id(self):
        self.prepare_data()
        url = '/oauth/authorize?response_type=code'
        rv = self.client.get(url)
        self.assertIn(b'invalid_client', rv.data)

        url = '/oauth/authorize?response_type=code&client_id=invalid'
        rv = self.client.get(url)
        self.assertIn(b'invalid_client', rv.data)

    def test_invalid_authorize(self):
        self.prepare_data()
        rv = self.client.post(self.authorize_url)
        self.assertIn('error=access_denied', rv.location)

        self.server.metadata = {'scopes_supported': ['profile']}
        rv = self.client.post(self.authorize_url + '&scope=invalid&state=foo')
        self.assertIn('error=invalid_scope', rv.location)
        self.assertIn('state=foo', rv.location)

    def test_unauthorized_client(self):
        self.prepare_data(True, 'token')
        rv = self.client.get(self.authorize_url)
        self.assertIn(b'unauthorized_client', rv.data)

    def test_invalid_client(self):
        self.prepare_data()
        rv = self.client.post('/oauth/token', data={
            'grant_type': 'authorization_code',
            'code': 'invalid',
            'client_id': 'invalid-id',
        })
        resp = json.loads(rv.data)
        self.assertEqual(resp['error'], 'invalid_client')

        headers = self.create_basic_header('code-client', 'invalid-secret')
        rv = self.client.post('/oauth/token', data={
            'grant_type': 'authorization_code',
            'code': 'invalid',
        }, headers=headers)
        resp = json.loads(rv.data)
        self.assertEqual(resp['error'], 'invalid_client')
        self.assertEqual(resp['error_uri'], 'https://a.b/e#invalid_client')

    def test_invalid_code(self):
        self.prepare_data()

        headers = self.create_basic_header('code-client', 'code-secret')
        rv = self.client.post('/oauth/token', data={
            'grant_type': 'authorization_code',
        }, headers=headers)
        resp = json.loads(rv.data)
        self.assertEqual(resp['error'], 'invalid_request')

        rv = self.client.post('/oauth/token', data={
            'grant_type': 'authorization_code',
            'code': 'invalid',
        }, headers=headers)
        resp = json.loads(rv.data)
        self.assertEqual(resp['error'], 'invalid_request')

        code = AuthorizationCode(
            code='no-user',
            client_id='code-client',
            user_id=0
        )
        db.session.add(code)
        db.session.commit()
        rv = self.client.post('/oauth/token', data={
            'grant_type': 'authorization_code',
            'code': 'no-user',
        }, headers=headers)
        resp = json.loads(rv.data)
        self.assertEqual(resp['error'], 'invalid_request')

    def test_invalid_redirect_uri(self):
        self.prepare_data()
        uri = self.authorize_url + '&redirect_uri=https%3A%2F%2Fa.c'
        rv = self.client.post(uri, data={'user_id': '1'})
        resp = json.loads(rv.data)
        self.assertEqual(resp['error'], 'invalid_request')

        uri = self.authorize_url + '&redirect_uri=https%3A%2F%2Fa.b'
        rv = self.client.post(uri, data={'user_id': '1'})
        self.assertIn('code=', rv.location)

        params = dict(url_decode(urlparse.urlparse(rv.location).query))
        code = params['code']
        headers = self.create_basic_header('code-client', 'code-secret')
        rv = self.client.post('/oauth/token', data={
            'grant_type': 'authorization_code',
            'code': code,
        }, headers=headers)
        resp = json.loads(rv.data)
        self.assertEqual(resp['error'], 'invalid_request')

    def test_invalid_grant_type(self):
        self.prepare_data(
            False, token_endpoint_auth_method='none',
            grant_type='invalid'
        )
        rv = self.client.post('/oauth/token', data={
            'grant_type': 'authorization_code',
            'client_id': 'code-client',
            'code': 'a',
        })
        resp = json.loads(rv.data)
        self.assertEqual(resp['error'], 'unauthorized_client')

    def test_authorize_token_no_refresh_token(self):
        self.app.config.update({'OAUTH2_REFRESH_TOKEN_GENERATOR': True})
        self.prepare_data(False, token_endpoint_auth_method='none')

        rv = self.client.post(self.authorize_url, data={'user_id': '1'})
        self.assertIn('code=', rv.location)

        params = dict(url_decode(urlparse.urlparse(rv.location).query))
        code = params['code']
        rv = self.client.post('/oauth/token', data={
            'grant_type': 'authorization_code',
            'code': code,
            'client_id': 'code-client',
        })
        resp = json.loads(rv.data)
        self.assertIn('access_token', resp)
        self.assertNotIn('refresh_token', resp)

    def test_authorize_token_has_refresh_token(self):
        # generate refresh token
        self.app.config.update({'OAUTH2_REFRESH_TOKEN_GENERATOR': True})
        self.prepare_data(grant_type='authorization_code\nrefresh_token')
        url = self.authorize_url + '&state=bar'
        rv = self.client.post(url, data={'user_id': '1'})
        self.assertIn('code=', rv.location)

        params = dict(url_decode(urlparse.urlparse(rv.location).query))
        self.assertEqual(params['state'], 'bar')

        code = params['code']
        headers = self.create_basic_header('code-client', 'code-secret')
        rv = self.client.post('/oauth/token', data={
            'grant_type': 'authorization_code',
            'code': code,
        }, headers=headers)
        resp = json.loads(rv.data)
        self.assertIn('access_token', resp)
        self.assertIn('refresh_token', resp)

    def test_client_secret_post(self):
        self.app.config.update({'OAUTH2_REFRESH_TOKEN_GENERATOR': True})
        self.prepare_data(
            grant_type='authorization_code\nrefresh_token',
            token_endpoint_auth_method='client_secret_post',
        )
        url = self.authorize_url + '&state=bar'
        rv = self.client.post(url, data={'user_id': '1'})
        self.assertIn('code=', rv.location)

        params = dict(url_decode(urlparse.urlparse(rv.location).query))
        self.assertEqual(params['state'], 'bar')

        code = params['code']
        rv = self.client.post('/oauth/token', data={
            'grant_type': 'authorization_code',
            'client_id': 'code-client',
            'client_secret': 'code-secret',
            'code': code,
        })
        resp = json.loads(rv.data)
        self.assertIn('access_token', resp)
        self.assertIn('refresh_token', resp)

    def test_token_generator(self):
        m = 'tests.flask.test_oauth2.oauth2_server:token_generator'
        self.app.config.update({'OAUTH2_ACCESS_TOKEN_GENERATOR': m})
        self.prepare_data(False, token_endpoint_auth_method='none')

        rv = self.client.post(self.authorize_url, data={'user_id': '1'})
        self.assertIn('code=', rv.location)

        params = dict(url_decode(urlparse.urlparse(rv.location).query))
        code = params['code']
        rv = self.client.post('/oauth/token', data={
            'grant_type': 'authorization_code',
            'code': code,
            'client_id': 'code-client',
        })
        resp = json.loads(rv.data)
        self.assertIn('access_token', resp)
        self.assertIn('c-authorization_code.1.', resp['access_token'])


class CacheAuthorizationCodeTest(AuthorizationCodeTest):
    LAZY_INIT = True

    def register_grant(self, server):

        def authenticate_user(authorization_code):
            return User.query.get(authorization_code.user_id)

        cache = SimpleCache()
        register_cache_authorization_code(cache, server, authenticate_user)
