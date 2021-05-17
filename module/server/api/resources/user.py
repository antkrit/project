"""Resource to work with user"""
from flask import request
from flask_restful import Resource
from flask_jwt_extended import (
    jwt_required,
    get_jwt,
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    decode_token
)
from module.server import messages
from module.server.models.user import User
from module.server.models.payment_cards import Card
from module.server.models.jwt_tokens import TokenBlocklist
from module.server.api.schemas.user import LoginSchema, RegisterSchema, AdminUserInfoSchema, FullUserInfoSchema
from module.server.api.schemas.payment_cards import UsedCardSchema, InputCardSchema


class UserAuthResource(Resource):
    """
    get:
        summary: Creates access and refresh tokens
        parameters:
            path: /api/v1/auth
            schema: LoginSchema
        responses:
            '200':
                 description: returns access, refresh tokens and information about access token(fresh, exp)
                 content:
                   application/json
            '400':
                 description: missing arguments
                 content:
                   application/json
            '401':
                 description: user doesn't exist or password doesn't match
                 content:
                    application/json
    post:
        summary: creates and saves to the database new user
        parameters:
            path: /api/v1/auth
            schema: RegisterSchema
        responses:
            '201':
                description: register new user
                content:
                    application/json
            '400':
                description: missing arguments or user already exists
                content:
                    application/json
            '403':
                description: current user is not admin
                content:
                    application/json
            '500':
                description: error saving to database
                content:
                    application/json
    """

    def get(self):
        """
        Creates an access_token and refresh_token for the user
        if user exists and login, password from the request match.
        """
        data = LoginSchema().load(request.get_json())

        login = data.get('login')
        password = data.get('password')

        user = User.get_user_by_username(login)

        if user and user.check_password(password):
            access_token = create_access_token(identity=user.uuid, fresh=True)
            refresh_token = create_refresh_token(user.uuid)
            decoded = decode_token(access_token)
            return {
                'access_token': access_token,
                'refresh_token': refresh_token,
                'fresh': decoded['fresh'],
                'expires_in': decoded['exp']
            }, 200
        return {'message': 'Unable to login.'}, 401

    @jwt_required()
    def post(self):
        """Creates new user and save it to the database. Available only for admin"""

        curr_user = User.get_by_uuid(get_jwt_identity())
        if curr_user.username != 'admin':
            return {'message': messages['access_denied']}, 403

        data = request.get_json()
        user = RegisterSchema().load(data)

        if User.get_user_by_username(data['username']):
            return {'message': 'This user already exists.'}, 400

        try:
            user.save_to_db()
            return {'message': messages['success_register']}, 201
        except ValueError as e:
            return {'message': messages['failure'] + ' Error - {0}'.format(e)}, 500


class LogoutUser(Resource):
    """
    post:
        summary: Creates access and refresh tokens
        parameters:
            - in: query
            path: /api/v1/logout
        responses:
            '200':
                description: user access_token was added to the blocklist
                content:
                   application/json
            '500':
                description: failed to save token in database
                content:
                    application/json
    """

    @jwt_required()
    def post(self):
        """Logout user. The user must be logged in first."""
        jti = get_jwt()['jti']
        user = User.get_by_uuid(get_jwt_identity())

        token = TokenBlocklist(user_id=user.id, jti=jti, reason='Logout')
        token.save_to_db()
        return {'message': messages['success']}, 200


class UserResource(Resource):
    """
    get:
        summary: returns user info
        parameters:
            path: /api/v1/users/<uuid>
            schemas: AdminUserInfoSchema, FullUserInfoSchema
        responses:
            '200':
                description: json representation of the user was returned
                content:
                    application/json
            '403':
                description: current user is not either admin or account holder
                content:
                    application/json
            '404':
                description: user not found
                content:
                    application/json
    post:
        summary: use payment card
        parameters:
            path: /api/v1/users/<uuid>
            schema: InputCardSchema
        responses:
            '200':
                description: the user's balance has been replenished
                content:
                    application/json
            '403':
                description: user is trying to replenish another balance
                content:
                    application/json
            '404':
                description: the card code is invalid or doesn't exist
                content:
                    application/json
    """
    @jwt_required()
    def get(self, uuid: str):
        """Returns info about user"""
        curr_user = User.get_by_uuid(get_jwt_identity())
        if curr_user.username != 'admin' and curr_user.uuid != uuid:
            return {'message': messages['access_denied']}, 403

        user_schema = AdminUserInfoSchema() if curr_user.username == 'admin' else FullUserInfoSchema()

        user = User.get_by_uuid(uuid)
        if user:
            return user_schema.dump(user), 200
        return {'message': messages['user_not_found']}, 404

    @jwt_required()
    def post(self, uuid: str):
        """Use card"""
        curr_user = User.get_by_uuid(get_jwt_identity())
        if curr_user.uuid != uuid:
            return {'message': messages['access_denied']}, 403

        data = InputCardSchema().load(request.get_json())
        if Card.get_card_by_code(data['code']):
            curr_user.use_card(data['code'])
            return {'message': messages['card_success_code']}, 200
        return {'message': messages['card_wrong_code']}, 404


class UserHistoryResource(Resource):
    """
    get:
        summary: returns user payment history
        parameters:
            path: /api/v1/users/<uuid>
            schema: UsedCardSchema
        responses:
            '200':
                description: user payment history was returned
                content:
                    application/json
    """
    @jwt_required()
    def get(self, uuid: str):
        """Returns user payment history"""
        curr_user = User.get_by_uuid(uuid)
        used_cards_schema = UsedCardSchema(many=True)

        if curr_user:
            history = curr_user.get_history()
            return used_cards_schema.dump(history), 200
        return {'message': messages['user_not_found']}, 404


class UsersResource(Resource):
    """
    get:
        summary: returns list of user or user info if user is not admin
        parameters:
            path: /api/v1/users
            schema: AdminUserInfoSchema, FullUserInfoSchema
        responses:
            '200':
                description: json list of users was returned
                content:
                    application/json
    """
    @jwt_required()
    def get(self):
        """Returns list of users if current user is admin, else user's account info"""
        curr_user = User.get_by_uuid(get_jwt_identity())
        if curr_user.username == 'admin':
            users_schema = AdminUserInfoSchema(many=True)
            all_users = User.query.all()
            return users_schema.dump(all_users), 200
        else:
            user_schema = FullUserInfoSchema()
            user = curr_user
            return user_schema.dump(user), 200


class TokenRefresh(Resource):
    """
    get:
        summary: creates new access and refresh token
        parameters:
            path: /api/v1/refresh
        responses:
            '200':
                description: token was refreshed
                content:
    """

    @jwt_required(refresh=True)
    def post(self):
        """Refresh access token"""
        current_id = get_jwt_identity()
        new_token = create_access_token(identity=current_id, fresh=False)
        new_refresh_token = create_refresh_token(current_id)
        decoded = decode_token(new_token)
        return {
            'access_token': new_token,
            'refresh_token': new_refresh_token,
            'fresh': decoded['fresh'],
            'expires_in': decoded['exp']
        }, 200

