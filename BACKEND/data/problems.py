import string
from random import random

import sqlalchemy

from .db_session import SqlAlchemyBase



class Problems(SqlAlchemyBase):
    __tablename__ = 'problems'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)

    version = sqlalchemy.Column(sqlalchemy.Text, nullable=True, default="0/0")
    section = sqlalchemy.Column(sqlalchemy.Text, nullable=True)
    type = sqlalchemy.Column(sqlalchemy.Text, nullable=True)
    perms = sqlalchemy.Column(sqlalchemy.JSON, nullable=True)
    url = sqlalchemy.Column(sqlalchemy.Text, nullable=True)

