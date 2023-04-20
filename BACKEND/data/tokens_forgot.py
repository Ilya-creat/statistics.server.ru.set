import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase


class TokensForgot(SqlAlchemyBase):
    __tablename__ = 'tokens_forgot'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    tokens = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    time = sqlalchemy.Column(sqlalchemy.DateTime,
                                  default=(datetime.datetime.now() + datetime.timedelta(hours=1)))
    status = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, default=1)
