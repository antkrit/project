"""Marshmallow schema for the user object"""
from marshmallow import Schema, fields, validate, post_load
from module import App
from module.server.models.user import User, Tariffs
from module.server.models.payment_cards import UsedCard


ma = App.ma


class AdminUserInfoSchema(ma.SQLAlchemyAutoSchema):
    """Schema for full admin info"""

    class Meta:
        model = User
        fields = (
            "username",
            "created_at",
            "ip",
            "name",
            "email",
            "phone",
            "tariff",
            "state",
            "balance",
            "_links",
        )
        load_only = ("password", "username", "phone", "email", "name")
        dump_only = ("created_at", "balance", "state", "ip", "_links")
        include_fk = True

    _links = ma.Hyperlinks(
        {
            "collection": ma.URLFor("api_users"),
            "self": ma.URLFor("api_user_details", values=dict(uuid="<uuid>")),
            "payment history": ma.URLFor("api_user_history", values=dict(uuid="<uuid>")),
            "moderate": ma.URLFor("api_admin_tools", values=dict(uuid="<uuid>")),
        }
    )


class FullUserInfoSchema(ma.SQLAlchemyAutoSchema):
    """Schema for full user info"""

    class Meta:
        model = User
        fields = (
            "username",
            "created_at",
            "ip",
            "name",
            "email",
            "phone",
            "tariff",
            "state",
            "balance",
            "address",
            "_links",
        )
        load_only = ("password",)
        dump_only = ("uuid", "created_at", "balance", "state", "ip", "_links")
        include_fk = True

    _links = ma.Hyperlinks(
        {
            "self": ma.URLFor("api_user_details", values=dict(uuid="<uuid>")),
            "payment history": ma.URLFor("api_user_history", values=dict(uuid="<uuid>")),
        }
    )


class LoginSchema(Schema):
    """Schema to parse data from the login request"""

    login = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)


class RegisterSchema(Schema):
    """Schema to parse data from the register request"""

    username = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)
    name = fields.Str(required=True)
    email = fields.Email()
    phone = fields.Str(required=True)
    address = fields.Str(required=True)
    tariff = fields.Str(
        required=True,
        validate=validate.OneOf([t.value["tariff_name"] for t in Tariffs]),
    )

    @post_load
    def create_new_user(self, data, **kwargs):
        return User(**data)
