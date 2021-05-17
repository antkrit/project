"""Resource for admin tools"""
from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from module.server import messages
from module.server.models.user import User
from module.server.api.schemas.admin import AdminChoiceSchema


class AdminToolsResource(Resource):
    """
    post:
    summary: work with user account. Available choices: ['activate', 'deactivate', 'delete']
    parameters:
        path: /api/v1/auth
        schema: RegisterSchema
    responses:
        '200':
            description: everything is okay
            content:
                application/json
        '400':
            description: missing arguments
            content:
                application/json
        '403':
            description: current user is not admin
            content:
                application/json
        '500':
            description: error deleting from database
            content:
                application/json
    """

    @jwt_required(fresh=True)
    def post(self, uuid):
        """Work with user account"""
        curr_user = User.get_by_uuid(get_jwt_identity())
        if curr_user.username != 'admin':
            return {'message': messages['access_denied']}, 403

        data = AdminChoiceSchema().load(request.get_json())
        user_to_work = User.get_by_uuid(uuid)

        if data['choice'] == 'activate':
            user_to_work.change_state()
            return {'message': messages['activate_state_success']}, 200
        elif data['choice'] == 'deactivate':
            user_to_work.change_state(deactivate=True)
            return {'message': messages['deactivate_state_success']}, 200
        elif data['choice'] == 'delete':
            try:
                user_to_work.delete_from_db()
                return {'message': messages['success']}, 200
            except Exception as e:
                return {'message': messages['failure'] + ' Error: {0}'.format(e)}, 500
