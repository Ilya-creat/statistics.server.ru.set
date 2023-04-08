from flask_login import UserMixin
from flask import url_for


class UserLogin(UserMixin):
    def fromDB(self, user_id, db):
        self.__user = db.getUser(user_id)
        return self

    def create(self, user):
        self.__user = user
        return self

    def get_id(self):
        return str(self.__user['id'])

    def get_user(self):
        return str(self.__user['user'])

    def get_email(self):
        return str(self.__user['email'])

    def get_status(self):
        return str(self.__user['status'])