import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase


class User(SqlAlchemyBase):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    user = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    email = sqlalchemy.Column(sqlalchemy.String,
                              index=True, unique=True, nullable=True)
    psw = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    timestamp = sqlalchemy.Column(sqlalchemy.DateTime,
                                  default=datetime.datetime.now)
    path_image = sqlalchemy.Column(sqlalchemy.String, default="user/img/default.jpg")
    status = sqlalchemy.Column(sqlalchemy.Integer, default=1)
    activate = sqlalchemy.Column(sqlalchemy.Integer,
                                 default=1)
