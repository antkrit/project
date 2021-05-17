"""Models for store jwt tokensr"""
from datetime import datetime
from module import App
from module.server.models import Base


db = App.db


class TokenBlocklist(Base, db.Model):
    """Block list table for saving expired JWT tokens"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    jti = db.Column(db.String(36), nullable=False)
    reason = db.Column(db.String, nullable=False, server_default="Token has expired.")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


@App.jwt.token_in_blocklist_loader
def check_if_token_in_blocklist(jwt_handler, jwt_payload):
    """Returns true if token in blocklist"""
    jti = jwt_payload["jti"]
    token = App.db.session.query(TokenBlocklist.id).filter_by(jti=jti).scalar()
    return token is not None
