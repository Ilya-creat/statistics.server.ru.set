import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase


class Posts(SqlAlchemyBase):
    __tablename__ = 'posts'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    content = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    times = sqlalchemy.Column(sqlalchemy.DateTime,
                                  default=(datetime.datetime.now() + datetime.timedelta(hours=1)))
    tags = sqlalchemy.Column(sqlalchemy.JSON, nullable=True, default={
        "type": []
    })
    authors = sqlalchemy.Column(sqlalchemy.JSON, nullable=True, default={
        "authors": [],
    })
