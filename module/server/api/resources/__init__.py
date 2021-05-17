"""Register api routes"""
from flask_restful import Api
from module.server.api.resources.user import (
    UserAuthResource, LogoutUser, UserResource, UsersResource, UserHistoryResource, TokenRefresh
)
from module.server.api.resources.admin import AdminToolsResource


api = Api(prefix='/api/v1')
api.add_resource(UserAuthResource, '/auth', endpoint='api_auth')
api.add_resource(LogoutUser, '/logout', endpoint='api_logout')
api.add_resource(TokenRefresh, '/refresh', endpoint='api_refresh')
api.add_resource(UsersResource, '/users', endpoint='api_users')
api.add_resource(UserResource, '/users/<uuid>', endpoint='api_user_details')
api.add_resource(UserHistoryResource, '/users/<uuid>/history', endpoint='api_user_history')
api.add_resource(AdminToolsResource, '/admin/users/<uuid>', endpoint='api_admin_tools')
