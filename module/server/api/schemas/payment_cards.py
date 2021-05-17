"""Marshmallow schemas for payment cards objects"""
from marshmallow import Schema, fields
from module import App
from module.server.models.payment_cards import Card, UsedCard


ma = App.ma


class CardSchema(ma.SQLAlchemyAutoSchema):
    """Schema for the payment card"""

    class Meta:
        model = Card
        fields = ('uuid', 'amount', 'code')
        dump_only = ('uuid',)


class UsedCardSchema(ma.SQLAlchemyAutoSchema):
    """Schema for used payment card"""

    class Meta:
        model = UsedCard
        fields = ('uuid', 'amount', 'code', 'used_at')
        dump_only = ('uuid', 'used_at')
        include_fk = True


class InputCardSchema(Schema):
    """Schema to receive payment card code"""
    code = fields.Str(required=True)
