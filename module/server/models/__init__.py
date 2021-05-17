"""Base classes and functions for models with common methods"""
from uuid import uuid4
from module import App


class Base:
    """Class with base methods"""

    @classmethod
    def get_by_uuid(cls, uuid: str):
        """
        Returns object by it's uuid if any, otherwise None
        :param uuid: uuid of the card
        """
        return cls.query.filter_by(uuid=uuid).first()

    def save_to_db(self):
        """Save object to db"""
        try:
            App.db.session.add(self)
            App.db.session.commit()
        except Exception as e:  # if unable to commit make rollback
            App.db.session.rollback()
            raise ValueError("Unable to save user: {0}".format(e))

    def delete_from_db(self):
        """Delete object from db"""
        try:
            App.db.session.delete(self)
            App.db.session.commit()
        except Exception as e:  # if unable to commit make rollback
            App.db.session.rollback()
            raise ValueError("Unable to delete user: {0}".format(e))


def generate_uuid():
    """Returns uuid with type string"""
    return str(uuid4())
