import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase


class Personal(SqlAlchemyBase):
    __tablename__ = 'personal'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    post = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    color = sqlalchemy.Column(sqlalchemy.String, nullable=True)