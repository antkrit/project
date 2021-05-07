"""Base classes for models with common methods"""


class BaseCard:
    """Base model for payment cards"""
    @classmethod
    def get_card_by_uuid(cls, uuid_code: str):
        """Returns card by it's uuid if any, otherwise None"""
        return cls.query.filter_by(uuid=uuid_code).first()

    @classmethod
    def get_card_by_code(cls, code: str):
        """Returns card by it's code if any, otherwise None"""
        return cls.query.get(code)
