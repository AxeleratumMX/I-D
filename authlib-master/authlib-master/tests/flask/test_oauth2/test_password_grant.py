from flask import json
from authlib.common.urls import add_params_to_uri
from authlib.oauth2.rfc6749.grants import (
    ResourceOwnerPasswordCredentialsGrant as _PasswordGrant,
)
from .models import db, User, Client
from .oauth2_server import TestCase
from .oauth2_server import create_authorization_server


class PasswordGrant(_PasswordGrant):
    def authenticate_user(self, username, password):
        user = User.query.filter_by(username=username).first()
        if user.check_password(password):
            return user


class PasswordTest(TestCase):
    def prepare_data(self, grant_type='password'):
        server = create_authorization_server(self.app)
        server.register_grant(PasswordGrant)
        self.server = server

        user = User(username='foo')
        db.session.add(user)
        db.session.commit()
        client = Client(
            user_id=user.id,
            client_id='password-client',
            client_secret='password-secret',
            redirect_uri='http://localhost/authorized',
            scope='profile',
            grant_type=grant_type,
        )
        db.session.add(client)
        db.session.commit()

    def test_invalid_client(self):
        self.prepare_data()
        rv = self.client.post('/oauth/token', data={
            'grant_type': 'password',
            'username': 'foo',
            'password': 'ok',
        })
        resp = json.loads(rv.data)
        self.assertEqual(resp['error'], 'invalid_client')

        headers = self.create_basic_header(
            'password-client', 'invalid-secret'
        )
        rv = self.client.post('/oauth/token', data={
            'grant_type': 'password',
            'username': 'foo',
            'password': 'ok',
        }, headers=headers)
        resp = json.loads(rv.data)
        self.assertEqual(resp['error'], 'invalid_client')

    def test_invalid_scope(self):
        self.prepare_data()
        self.server.metadata = {'scopes_supported': ['profile']}
        headers = self.create_basic_header(
            'password-client', 'password-secret'
        )
        rv = self.client.post('/oauth/token', data={
            'grant_type': 'password',
            'username': 'foo',
            'password': 'ok',
            'scope': 'invalid',
        }, headers=headers)
        resp = json.loads(rv.data)
        self.assertEqual(resp['error'], 'invalid_scope')

    def test_invalid_request(self):
        self.prepare_data()
        headers = self.create_basic_header(
            'password-client', 'password-secret'
        )

        rv = self.client.get(add_params_to_uri('/oauth/token', {
            'grant_type': 'password',
        }), headers=headers)
        resp = json.loads(rv.data)
        self.assertEqual(resp['error'], 'invalid_grant')

        rv = self.client.post('/oauth/token', data={
            'grant_type': 'password',
        }, headers=headers)
        resp = json.loads(rv.data)
        self.assertEqual(resp['error'], 'invalid_request')

        rv = self.client.post('/oauth/token', data={
            'grant_type': 'password',
            'username': 'foo',
        }, headers=headers)
        resp = json.loads(rv.data)
        self.assertEqual(resp['error'], 'invalid_request')

        rv = self.client.post('/oauth/token', data={
            'grant_type': 'password',
            'username': 'foo',
            'password': 'wrong',
        }, headers=headers)
        resp = json.loads(rv.data)
        self.assertEqual(resp['error'], 'invalid_grant')

    def test_invalid_grant_type(self):
        self.prepare_data(grant_type='invalid')
        headers = self.create_basic_header(
            'password-client', 'password-secret'
        )
        rv = self.client.post('/oauth/token', data={
            'grant_type': 'password',
            'username': 'foo',
            'password': 'ok',
        }, headers=headers)
        resp = json.loads(rv.data)
        self.assertEqual(resp['error'], 'unauthorized_client')

    def test_authorize_token(self):
        self.prepare_data()
        headers = self.create_basic_header(
            'password-client', 'password-secret'
        )
        rv = self.client.post('/oauth/token', data={
            'grant_type': 'password',
            'username': 'foo',
            'password': 'ok',
        }, headers=headers)
        resp = json.loads(rv.data)
        self.assertIn('access_token', resp)

    def test_token_generator(self):
        m = 'tests.flask.test_oauth2.oauth2_server:token_generator'
        self.app.config.update({'OAUTH2_ACCESS_TOKEN_GENERATOR': m})
        self.prepare_data()
        headers = self.create_basic_header(
            'password-client', 'password-secret'
        )
        rv = self.client.post('/oauth/token', data={
            'grant_type': 'password',
            'username': 'foo',
            'password': 'ok',
        }, headers=headers)
        resp = json.loads(rv.data)
        self.assertIn('access_token', resp)
        self.assertIn('p-password.1.', resp['access_token'])

    def test_custom_expires_in(self):
        self.app.config.update({
            'OAUTH2_TOKEN_EXPIRES_IN': {'password': 1800}
        })
        self.prepare_data()
        headers = self.create_basic_header(
            'password-client', 'password-secret'
        )
        rv = self.client.post('/oauth/token', data={
            'grant_type': 'password',
            'username': 'foo',
            'password': 'ok',
        }, headers=headers)
        resp = json.loads(rv.data)
        self.assertIn('access_token', resp)
        self.assertEqual(resp['expires_in'], 1800)
