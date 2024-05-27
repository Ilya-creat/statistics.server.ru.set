import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase


class Posts(SqlAlchemyBase):
    __tablename__ = 'posts'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name_ru = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    name_en = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    sub_content_ru = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    sub_content_en = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    content_ru = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    content_en = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    times = sqlalchemy.Column(sqlalchemy.DateTime,
                                  default=(datetime.datetime.now() + datetime.timedelta(hours=1)))
    tags = sqlalchemy.Column(sqlalchemy.JSON, nullable=True, default={
        "type": []
    })
    authors = sqlalchemy.Column(sqlalchemy.JSON, nullable=True, default={
        "authors": [],
    })
    status = sqlalchemy.Column(sqlalchemy.Integer, default=0)
