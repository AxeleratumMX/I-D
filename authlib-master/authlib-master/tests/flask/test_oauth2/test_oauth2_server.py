from flask import json, jsonify
from authlib.flask.oauth2 import ResourceProtector, current_token
from authlib.flask.oauth2.sqla import create_bearer_token_validator
from .models import db, User, Client, Token
from .oauth2_server import TestCase
from .oauth2_server import create_authorization_server

require_oauth = ResourceProtector()
BearerTokenValidator = create_bearer_token_validator(db.session, Token)
require_oauth.register_token_validator(BearerTokenValidator())


def create_resource_server(app):
    @app.route('/user')
    @require_oauth('profile')
    def user_profile():
        user = current_token.user
        return jsonify(id=user.id, username=user.username)

    @app.route('/user/email')
    @require_oauth('email')
    def user_email():
        user = current_token.user
        return jsonify(email=user.username + '@example.com')

    @app.route('/info')
    @require_oauth()
    def public_info():
        return jsonify(status='ok')

    @app.route('/operator-and')
    @require_oauth('profile email', 'AND')
    def operator_and():
        return jsonify(status='ok')

    @app.route('/operator-or')
    @require_oauth('profile email', 'OR')
    def operator_or():
        return jsonify(status='ok')

    def scope_operator(token_scopes, resource_scopes):
        return 'profile' in token_scopes and 'email' not in token_scopes

    @app.route('/operator-func')
    @require_oauth(operator=scope_operator)
    def operator_func():
        return jsonify(status='ok')

    @app.route('/acquire')
    def test_acquire():
        with require_oauth.acquire('profile') as token:
            user = token.user
            return jsonify(id=user.id, username=user.username)

    @app.route('/optional')
    @require_oauth('profile', optional=True)
    def test_optional_token():
        if current_token:
            user = current_token.user
            return jsonify(id=user.id, username=user.username)
        else:
            return jsonify(id=0, username='anonymous')


class AuthorizationTest(TestCase):
    def test_none_grant(self):
        create_authorization_server(self.app)
        authorize_url = (
            '/oauth/authorize?response_type=token'
            '&client_id=implicit-client'
        )
        rv = self.client.get(authorize_url)
        self.assertIn(b'invalid_grant', rv.data)

        rv = self.client.post(authorize_url, data={'user_id': '1'})
        self.assertNotEqual(rv.status, 200)

        rv = self.client.post('/oauth/token', data={
            'grant_type': 'authorization_code',
            'code': 'x',
        })
        data = json.loads(rv.data)
        self.assertEqual(data['error'], 'invalid_grant')


class ResourceTest(TestCase):
    def prepare_data(self):
        create_resource_server(self.app)

        user = User(username='foo')
        db.session.add(user)
        db.session.commit()
        client = Client(
            user_id=user.id,
            client_id='resource-client',
            client_secret='resource-secret',
            redirect_uri='http://localhost/authorized',
            scope='profile',
        )
        db.session.add(client)
        db.session.commit()

    def create_token(self, expires_in=3600):
        token = Token(
            user_id=1,
            client_id='resource-client',
            token_type='bearer',
            access_token='a1',
            scope='profile',
            expires_in=expires_in,
        )
        db.session.add(token)
        db.session.commit()

    def create_bearer_header(self, token):
        return {'Authorization': 'Bearer ' + token}

    def test_invalid_token(self):
        self.prepare_data()

        rv = self.client.get('/user')
        self.assertEqual(rv.status_code, 401)
        resp = json.loads(rv.data)
        self.assertEqual(resp['error'], 'missing_authorization')

        headers = {'Authorization': 'invalid token'}
        rv = self.client.get('/user', headers=headers)
        self.assertEqual(rv.status_code, 401)
        resp = json.loads(rv.data)
        self.assertEqual(resp['error'], 'unsupported_token_type')

        headers = self.create_bearer_header('invalid')
        rv = self.client.get('/user', headers=headers)
        self.assertEqual(rv.status_code, 401)
        resp = json.loads(rv.data)
        self.assertEqual(resp['error'], 'invalid_token')

    def test_expired_token(self):
        self.prepare_data()
        self.create_token(0)
        headers = self.create_bearer_header('a1')

        rv = self.client.get('/user', headers=headers)
        self.assertEqual(rv.status_code, 401)
        resp = json.loads(rv.data)
        self.assertEqual(resp['error'], 'invalid_token')

        rv = self.client.get('/acquire', headers=headers)
        self.assertEqual(rv.status_code, 401)

    def test_insufficient_token(self):
        self.prepare_data()
        self.create_token()
        headers = self.create_bearer_header('a1')
        rv = self.client.get('/user/email', headers=headers)
        self.assertEqual(rv.status_code, 403)
        resp = json.loads(rv.data)
        self.assertEqual(resp['error'], 'insufficient_scope')

    def test_access_resource(self):
        self.prepare_data()
        self.create_token()
        headers = self.create_bearer_header('a1')

        rv = self.client.get('/user', headers=headers)
        resp = json.loads(rv.data)
        self.assertEqual(resp['username'], 'foo')

        rv = self.client.get('/acquire', headers=headers)
        resp = json.loads(rv.data)
        self.assertEqual(resp['username'], 'foo')

        rv = self.client.get('/info', headers=headers)
        resp = json.loads(rv.data)
        self.assertEqual(resp['status'], 'ok')

    def test_scope_operator(self):
        self.prepare_data()
        self.create_token()
        headers = self.create_bearer_header('a1')
        rv = self.client.get('/operator-and', headers=headers)
        self.assertEqual(rv.status_code, 403)
        resp = json.loads(rv.data)
        self.assertEqual(resp['error'], 'insufficient_scope')

        rv = self.client.get('/operator-or', headers=headers)
        self.assertEqual(rv.status_code, 200)

        rv = self.client.get('/operator-func', headers=headers)
        self.assertEqual(rv.status_code, 200)

    def test_optional_token(self):
        self.prepare_data()
        rv = self.client.get('/optional')
        self.assertEqual(rv.status_code, 200)
        resp = json.loads(rv.data)
        self.assertEqual(resp['username'], 'anonymous')

        self.create_token()
        headers = self.create_bearer_header('a1')
        rv = self.client.get('/optional', headers=headers)
        self.assertEqual(rv.status_code, 200)
        resp = json.loads(rv.data)
        self.assertEqual(resp['username'], 'foo')
