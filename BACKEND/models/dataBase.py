import configparser
import datetime
import sqlite3
from os import listdir
from os.path import isfile
from shlex import join

import requests
from PIL import Image, ImageSequence

from BACKEND.data import db_session
from BACKEND.data.posts import Posts
from BACKEND.data.tokens_forgot import TokensForgot
from BACKEND.data.users import User
from BACKEND.data.personal import Personal
from BACKEND.models.validate import generation_token
import os


class DATABASE:
    def __init__(self, db):
        self.db_session = db_session
        self.db_session.global_init(db)

    def check_register_by_login(self, login):
        try:
            db_sess = self.db_session.create_session()
            if db_sess.query(User).filter(User.user == login).first():
                # print(f'Пользователь с таким {forms} уже существует. . .')
                return False
            else:
                return True
        except sqlite3.Error as e:
            print("Ошибка получения запроса в БД:\n" + str(e))
            return False

    def check_register_by_email(self, email):
        try:
            db_sess = self.db_session.create_session()
            if db_sess.query(User).filter(User.email == email).first():
                # print(f'Пользователь с таким {forms} уже существует. . .')
                return False
            else:
                return True
        except sqlite3.Error as e:
            print("Ошибка получения запроса в БД:\n" + str(e))
            return False

    def add_user(self, login, name, email, hpsw):
        try:
            db_sess = self.db_session.create_session()
            if db_sess.query(User).filter(User.email == email).first():
                # print('Пользователь с таким email уже существует. . .')
                return False
            user = User()
            user.user = login
            user.name = name
            user.email = email
            user.psw = hpsw
            db_sess.add(user)
            db_sess.commit()
            return True
        except sqlite3.Error as e:
            print("Ошибка добавления пользователя в БД:\n" + str(e))
            return False

    def get_user_by_email(self, email):
        try:
            db_sess = self.db_session.create_session()
            user = db_sess.query(User).filter(User.email == email).first()
            if not user:
                # print("Пользователь не найден")
                return False
            return user
        except sqlite3.Error as e:
            print("Ошибка получения данных из БД:\n" + str(e))
        return False

    def get_user_by_login(self, login):
        try:
            db_sess = self.db_session.create_session()
            user = db_sess.query(User).filter(User.user == login).first()
            if not user:
                # print("Пользователь не найден")
                return False
            return user
        except sqlite3.Error as e:
            print("Ошибка получения данных из БД:\n" + str(e))
        return False

    def get_user(self, user_id):
        try:
            db_sess = self.db_session.create_session()
            user = db_sess.query(User).filter(User.id == user_id).first()
            if not user:
                # print("Пользователь не найден")
                return False
            return user
        except sqlite3.Error as e:
            print("Ошибка получения данных из БД:\n" + str(e))
        return False

    def task_converter(self, _id):
        try:
            self.__cur.execute(f"SELECT name FROM task_converter WHERE id = '{_id}'")
            ans = self.__cur.fetchone()
            return ans[0]
        except sqlite3.Error as e:
            print("Ошибка получения данных из БД (task_converter):\n" + str(e))
            return None

    def create(self, contest_id, user_id, task_id):
        try:
            self.__cur.execute(f"INSERT INTO code_task VALUES(NULL, ?, ?, ?, ?, ?, ?, ?, NULL, NULL, NULL, 0, NULL)",
                               (datetime.datetime.now(), task_id, user_id, contest_id, 'No protocole', '-', 'Wait...'))
            self.__db.commit()
            self.__cur.execute(f"SELECT id FROM code_task ORDER BY id DESC LIMIT 1")
            _id = self.__cur.fetchone()
            return _id[0]
        except sqlite3.Error as e:
            print("Ошибка создания данных БД (create):\n" + str(e))
            return None

    def compile_lang(self, db, lang):
        try:
            self.__cur.execute(f"UPDATE code_task SET lang = '{lang}' WHERE id = '{db}'")
            self.__db.commit()
            return True
        except sqlite3.Error as e:
            print("Ошибка создания данных БД (create):\n" + str(e))
            return None

    def get_testing_result(self, _id, tasks, contest):
        try:
            self.__cur.execute(f"SELECT * FROM code_task WHERE user_id = '{_id}' and contest = '{contest}'")
            ans = self.__cur.fetchall()
            result = []
            json_f = {}
            for i in ans:
                ok = []
                if i[2] in tasks:
                    for j in i:
                        ok.append(j)
                    config = configparser.ConfigParser()
                    config.read(f'instance/task/{self.task_converter(ok[2])}/config.ini', encoding="utf-8")  # чтение
                    ok[2] = [ok[2], config['Config']['name']]
                    result.append(ok)
            return result
        except sqlite3.Error as e:
            print("Ошибка получения данных из БД (get_testing_result):\n" + str(e))
            return None

    def get_testing_result_full(self, tasks, contest):
        try:
            self.__cur.execute(f"SELECT * FROM code_task WHERE contest = '{contest}'")
            ans = self.__cur.fetchall()
            result = []
            json_f = {}
            for i in ans:
                ok = []
                if i[2] in tasks:
                    for j in i:
                        ok.append(j)
                    config = configparser.ConfigParser()
                    config.read(f'instance/task/{self.task_converter(ok[2])}/config.ini', encoding="utf-8")  # чтение
                    ok[2] = [ok[2], config['Config']['name']]
                    result.append(ok)
            return result
        except sqlite3.Error as e:
            print("Ошибка получения данных из БД (get_testing_result_full):\n" + str(e))
            return None

    def overwrite_password(self, user_id, password):
        try:
            db_sess = self.db_session.create_session()
            user = db_sess.query(User).filter(User.id == user_id).first()
            user.psw = password
            db_sess.commit()
            return True
        except Exception as e:
            print("Ошибка обновления данных в БД (overwrite_password):\n" + str(e))
            return False

    def add_token_forgot(self, user_id):
        try:
            db_sess = self.db_session.create_session()
            token = TokensForgot()
            token.tokens = generation_token()
            token.user_id = user_id
            db_sess.add(token)
            db_sess.commit()
            return token.tokens
        except Exception as e:
            print("Ошибка создания данных в БД (add_token_forgot):\n" + str(e))
            return False

    def check_session_token(self, token):
        try:
            db_sess = self.db_session.create_session()
            result = db_sess.query(TokensForgot).filter(TokensForgot.tokens == token).first()
            # print(result.time, result.status, result.time > datetime.datetime.now())
            if result.status and \
                    result.time > datetime.datetime.now():
                return True
            else:
                return False
        except Exception as e:
            print("Ошибка получения данных из БД (check_session_token):\n" + str(e))
            return False

    def close_session_token(self, token):
        try:
            db_sess = self.db_session.create_session()
            result = db_sess.query(TokensForgot).filter(TokensForgot.tokens == token).first()
            result.status = 0
            db_sess.add(result)
            db_sess.commit()
            return True
        except Exception as e:
            print("Ошибка получения данных из БД (close_session_token):\n" + str(e))
            return False

    def get_user_by_token_forgot(self, token):
        try:
            db_sess = self.db_session.create_session()
            result = db_sess.query(TokensForgot).filter(TokensForgot.tokens == token).first()
            return result.user_id
        except Exception as e:
            print("Ошибка получения данных из БД (get_user_by_token_forgot):\n" + str(e))
            return False

    def get_status_info(self, status_id):
        try:
            db_sess = self.db_session.create_session()
            result = db_sess.query(Personal).filter(Personal.id == status_id).first()
            return result.post
        except Exception as e:
            print("Ошибка получения данных из БД (get_status_info):\n" + str(e))
            return False

    def upload_data(self, user_id, name=None, photo=None):
        try:
            # print(user_id, photo)
            db_sess = self.db_session.create_session()
            user = db_sess.query(User).filter(User.id == user_id).first()
            if photo:
                only_files = [f for f in listdir(f"{os.getcwd()}/WEB/static/user/img")]
                for i in range(len(only_files)):
                    only_files[i] = only_files[i].split('.')[0]
                import random
                import string
                text = [random.choice(string.ascii_lowercase + string.digits if i != 5 else string.ascii_uppercase) for
                        i in range(10)]
                res = ''.join(text)
                while res in only_files:
                    text = [random.choice(string.ascii_lowercase + string.digits if i != 5 else string.ascii_uppercase)
                            for
                            i in range(10)]
                    res = ''.join(text)
                picture = Image.open(photo)
                if photo.filename.split('.')[1] == 'gif':
                    frames = [frame.copy() for frame in ImageSequence.Iterator(picture)]
                    picture.save(open(f"{os.getcwd()}/WEB/static/user/img/{res}.{photo.filename.split('.')[1]}", "wb"),
                                 save_all=True, append_images=frames, duration=100, loop=0)
                else:
                    picture.save(f"{os.getcwd()}/WEB/static/user/img/{res}.{photo.filename.split('.')[1]}")
                if user.path_image.split('/')[-1] != 'default.jpg':
                    os.remove(f"{os.getcwd()}/WEB/static/{user.path_image}")
                # print(f"user/img/{res}.{photo.filename.split('.')[1]}")
                user.path_image = f"user/img/{res}.{photo.filename.split('.')[1]}"
            if name:
                user.name = name
            db_sess.add(user)
            db_sess.commit()
            return True
        except Exception as e:
            print("Ошибка обновления данных в БД (upload_data):\n" + str(e))
            return False

    def get_color(self, status_id):
        try:
            db_sess = self.db_session.create_session()
            result = db_sess.query(Personal).filter(Personal.id == status_id).first()
            return result.color
        except Exception as e:
            print("Ошибка получения данных из БД (get_color):\n" + str(e))
            return False

    def get_posts(self):
        try:
            db_sess = self.db_session.create_session()
            result = db_sess.query(Posts).all()
            return result
        except Exception as e:
            print("Ошибка получения данных из БД (get_posts):\n" + str(e))
            return None