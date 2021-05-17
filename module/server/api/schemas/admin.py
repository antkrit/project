"""Marshmallow schema for admin tools"""
from marshmallow import Schema, fields, validate


class AdminChoiceSchema(Schema):
    """Scheme to get the administrator's choice"""
    choice = fields.Str(required=True, validate=validate.OneOf(['activate', 'deactivate', 'delete']))
