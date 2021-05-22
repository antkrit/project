"""Test jwt_token model and methods"""
from flask_jwt_extended import create_access_token, decode_token
from module.tests import setup_database, dataset
from module.server.models.jwt_tokens import check_if_token_in_blocklist, TokenBlocklist


def test_check_if_token_in_blocklist(dataset):
    """Checks loading jwt from blocklist"""

    db = dataset

    decoded = decode_token(create_access_token(identity=1))
    token = TokenBlocklist(user_id=1, jti=decoded["jti"])
    token.save_to_db()

    assert check_if_token_in_blocklist(jwt_handler=None, jwt_payload={"jti": decoded["jti"]})
