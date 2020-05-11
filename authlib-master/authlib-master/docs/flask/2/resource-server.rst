.. _flask_oauth2_resource_protector:

Resource Server
===============

Protect users resources, so that only the authorized clients with the
authorized access token can access the given scope resources.

A resource server can be a different server other than the authorization
server. Here is the way to protect your users' resources::

    from flask import jsonify
    from authlib.flask.oauth2 import ResourceProtector, current_token
    from authlib.oauth2.rfc6750 import BearerTokenValidator

    class MyBearerTokenValidator(BearerTokenValidator):
        def authenticate_token(self, token_string):
            return Token.query.filter_by(access_token=token_string).first()

        def request_invalid(self, request):
            return False

        def token_revoked(self, token):
            return token.revoked

    require_oauth = ResourceProtector()

    # only bearer token is supported currently
    require_oauth.register_token_validator(MyBearerTokenValidator())

    # you can also create BearerTokenValidator with shortcut
    from authlib.flask.oauth2.sqla import create_bearer_token_validator

    BearerTokenValidator = create_bearer_token_validator(db.session, Token)
    require_oauth.register_token_validator(BearerTokenValidator())

    @app.route('/user')
    @require_oauth('profile')
    def user_profile():
        user = current_token.user
        return jsonify(user)

If the resource is not protected by a scope, use ``None``::

    @app.route('/user')
    @require_oauth()
    def user_profile():
        user = current_token.user
        return jsonify(user)

    # or with None

    @app.route('/user')
    @require_oauth(None)
    def user_profile():
        user = current_token.user
        return jsonify(user)

The ``current_token`` is a proxy to the Token model you have defined above.
Since there is a ``user`` relationship on the Token model, we can access this
``user`` with ``current_token.user``.

If decorator is not your favorite, there is a ``with`` statement for you::

    @app.route('/user')
    def user_profile():
        with require_oauth.acquire('profile') as token:
            user = token.user
            return jsonify(user)

.. _flask_oauth2_multiple_scopes:

Multiple Scopes
---------------

You can apply multiple scopes to one endpoint in **AND** and **OR** modes.
The default is **AND** mode.

.. code-block:: python

    @app.route('/profile')
    @require_oauth('profile email', 'AND')
    def user_profile():
        user = current_token.user
        return jsonify(user)

It requires the token containing both ``profile`` and ``email`` scope.

.. code-block:: python

    @app.route('/profile')
    @require_oauth('profile email', 'OR')
    def user_profile():
        user = current_token.user
        return jsonify(user)

It requires the token containing either ``profile`` or ``email`` scope.

It is also possible to pass a function as the scope operator. e.g.::

    def scope_operator(token_scopes, resource_scopes):
        # this equals "AND"
        return token_scopes.issuperset(resource_scopes)

    @app.route('/profile')
    @require_oauth('profile email', scope_operator)
    def user_profile():
        user = current_token.user
        return jsonify(user)


MethodView & Flask-Restful
--------------------------

You can also use the ``require_oauth`` decorator in ``flask.views.MethodView``
and ``flask_restful.Resource``::

    from flask.views import MethodView

    class UserAPI(MethodView):
        decorators = [require_oauth('profile')]


    from flask_restful import Resource

    class UserAPI(Resource):
        method_decorators = [require_oauth('profile')]

