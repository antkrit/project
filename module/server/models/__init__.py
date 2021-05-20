"""Base classes and functions for models with common methods"""
from uuid import uuid4
from module import App


class Base:
    """Class with base methods"""

    @classmethod
    def get_by_uuid(cls, uuid):
        """
        Returns object by it's uuid if any, otherwise None
        :param uuid: uuid of the object
        :type uuid: str
        """
        return cls.query.filter_by(uuid=uuid).first()

    def save_to_db(self):
        """
        Save object to db
        :raises ValueError: the object cannot be saved in the database
        """
        try:
            App.db.session.add(self)
            App.db.session.commit()
        except Exception as save_err:  # if unable to commit make rollback
            App.db.session.rollback()
            raise ValueError("Unable to save user: {0}".format(save_err)) from save_err

    def delete_from_db(self):
        """
        Delete object from db
        :raises ValueError: the object cannot be deleted from the database
        """
        try:
            App.db.session.delete(self)
            App.db.session.commit()
        except Exception as del_err:  # if unable to commit make rollback
            App.db.session.rollback()
            raise ValueError("Unable to delete user: {0}".format(del_err)) from del_err


def generate_uuid():
    """Returns random uuid with type 'string'"""
    return str(uuid4())
