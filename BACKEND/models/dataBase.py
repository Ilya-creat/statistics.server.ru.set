import configparser
import datetime
import json
import random
import sqlite3
import string
import time
from os import listdir
from os.path import isfile
from shlex import join

import requests
from PIL import Image, ImageSequence
from pathlib import Path

from BACKEND.data import db_session
from BACKEND.data.posts import Posts
from BACKEND.data.tokens_forgot import TokensForgot
from BACKEND.data.problems import Problems
from BACKEND.data.users import User
from BACKEND.models.config import PATH
from BACKEND.models.validate import generation_token
import os
from pathlib import Path


class DATABASE:
    def __init__(self, db):
        if type(db) != sqlite3.Connection:
            self.__db = sqlite3.Connection(db, check_same_thread=False)

            self.__cur = self.__db.cursor()

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

    def upload_data(self, user_id, name=None, photo=None):
        try:
            # print(user_id, photo)
            db_sess = self.db_session.create_session()
            user = db_sess.query(User).filter(User.id == user_id).first()
            if photo:
                only_files = [f for f in listdir(f"{os.path.abspath(os.curdir)}/WEB/static/user/img")]
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
                    picture.save(open(f"{PATH}/WEB/static/user/img/{res}.{photo.filename.split('.')[1]}", "wb"),
                                 save_all=True, append_images=frames, duration=100, loop=0)
                else:
                    picture.save(f"{PATH}/WEB/static/user/img/{res}.{photo.filename.split('.')[1]}")
                if user.path_image.split('/')[-1] != 'default.jpg':
                    os.remove(f"{PATH}/WEB/static/{user.path_image}")
                user.path_image = f"user/img/{res}.{photo.filename.split('.')[1]}"
            if name:
                user.name = name
            db_sess.add(user)
            db_sess.commit()
            return True
        except Exception as e:
            print("Ошибка обновления данных в БД (upload_data):\n" + str(e))
            return False

    def get_posts(self):
        try:
            db_sess = self.db_session.create_session()
            result = db_sess.query(Posts).filter(Posts.status == 1).all()
            return result
        except Exception as e:
            print("Ошибка получения данных из БД (get_posts):\n" + str(e))
            return None

    def get_post(self, id_):
        try:
            db_sess = self.db_session.create_session()
            result = db_sess.query(Posts).filter(Posts.id == id_).first()
            return result
        except Exception as e:
            print("Ошибка получения данных из БД (get_post):\n" + str(e))
            return None

    def create_problem(self, section_problem, type_problem, id_):
        try:
            db_sess = self.db_session.create_session()
            db_sess_t = self.db_session.create_session()
            res = db_sess_t.query(Problems.url).all()
            text = ''.join(random.sample(string.ascii_uppercase + string.ascii_lowercase, k=random.randint(7, 20)))
            print(res)
            while (text,) in res:
                text = ''.join(random.sample(string.ascii_uppercase + string.ascii_lowercase, k=random.randint(7, 20)))
            c_problem = Problems()
            c_problem.section = section_problem
            c_problem.type = type_problem
            c_problem.perms = {
                "users": {
                    "x": [id_],
                    "r": [],
                    "w": [],
                    "rw+": []
                }
            }
            c_problem.url = text
            db_sess.add(c_problem)
            db_sess.commit()
            if self.create_problem_directory(section_problem, type_problem, text):
                return True
            else:
                return False
        except Exception as e:
            print("Ошибка создания данных в БД (create_problem):\n" + str(e))
            return False

    def create_problem_directory(self, sector_problem, type_problem, url_problem):
        try:
            if sector_problem == ".sport-programming" and type_problem == ".standard":
                Path(f"{PATH}/BACKEND/problems/problems_edit/{url_problem}").mkdir(parents=True, exist_ok=True)
                Path(f"{PATH}/BACKEND/problems/problems_edit/{url_problem}/scripts").mkdir(parents=True, exist_ok=True)
                Path(f"{PATH}/BACKEND/problems/problems_edit/{url_problem}/scripts/validator").mkdir(parents=True,
                                                                                                     exist_ok=True)
                Path(f"{PATH}/BACKEND/problems/problems_edit/{url_problem}/scripts/checker").mkdir(parents=True,
                                                                                                   exist_ok=True)
                Path(f"{PATH}/BACKEND/problems/problems_edit/{url_problem}/scripts/gen").mkdir(parents=True,
                                                                                               exist_ok=True)
                Path(f"{PATH}/BACKEND/problems/problems_edit/{url_problem}/solutions").mkdir(parents=True,
                                                                                             exist_ok=True)
                Path(f"{PATH}/BACKEND/problems/problems_edit/{url_problem}/tests").mkdir(parents=True, exist_ok=True)
                Path(f"{PATH}/BACKEND/problems/problems_edit/{url_problem}/statements").mkdir(parents=True,
                                                                                              exist_ok=True)
                Path(f"{PATH}/BACKEND/problems/problems_edit/{url_problem}/statements/name.md").touch(mode=0o644)
                Path(f"{PATH}/BACKEND/problems/problems_edit/{url_problem}/statements/legend.md").touch(mode=0o644)
                Path(f"{PATH}/BACKEND/problems/problems_edit/{url_problem}/statements/input.md").touch(mode=0o644)
                Path(f"{PATH}/BACKEND/problems/problems_edit/{url_problem}/statements/output.md").touch(mode=0o644)
                Path(f"{PATH}/BACKEND/problems/problems_edit/{url_problem}/statements/score.md").touch(mode=0o644)
                Path(f"{PATH}/BACKEND/problems/problems_edit/{url_problem}/statements/note.md").touch(mode=0o644)

                Path(f"{PATH}/BACKEND/problems/problems_edit/{url_problem}/config.json").touch(mode=0o644)
                with open(f"{PATH}/BACKEND/problems/problems_edit/{url_problem}/config.json", "w+") as config:
                    config_file = {
                        "config": {
                            "name": "",
                            "resources": {
                                "stdin": "stdin",
                                "stdout": "stdout",
                                "time-limit-exceed": 1000,
                                "memory-limit-exceed": 256
                            },
                            "scripts": {
                                "validator": "",
                                "checker": "",
                                "gen": "",
                            },
                            "tags": [],
                            "examples": [],
                            "admin-verify-out": [],
                            "testing": {
                                "format": "",
                                "groups": {
                                },
                                "group-testing": [],
                                "each-test": {
                                },
                                "each-test-testing": []
                            }
                        }
                    }
                    json.dump(config_file, config, indent=4)
            return True
        except Exception as e:
            print("Ошибка создания директории или файла (create_problem_directory):\n" + str(e))
            return False

    def get_user_problems(self, user_id, lang="ru"):
        try:
            db_sess = self.db_session.create_session()
            result_full = db_sess.query(Problems).all()
            result = []
            for item in result_full:
                if user_id in item.perms["users"]["x"] or user_id in item.perms["users"]["r"] or \
                        user_id in item.perms["users"]["w"] or user_id in item.perms["users"]["rw+"]:
                    json_l, text_n = None, None
                    try:
                        with open(f"{PATH}/BACKEND/problems/problems_edit/{item.url}/config.json", "r") as file:
                            json_l = json.load(file)
                            # print(json_l)
                        with open(f"{PATH}/BACKEND/problems/problems_edit/{item.url}/statements/{lang}/name.md", "r") as file:
                            text_n = file.read()
                        result.append([item, json_l["config"]["name"], text_n])
                    except Exception:
                        result.append([item, None, None])
            return result
        except Exception as e:
            print("Ошибка получения данных из БД (get_user_problems):\n" + str(e))
            return []

    def get_user_problem_permissions(self, problems_id):
        try:
            db_sess = self.db_session.create_session()
            result = db_sess.query(Problems.perms).filter(Problems.url == problems_id).first()
            return result[0]
        except Exception as e:
            print("Ошибка получения данных из БД (get_user_problems):\n" + str(e))
            return {}

    def get_problem_info(self, problem_url):
        try:
            db_sess = self.db_session.create_session()
            result = db_sess.query(Problems).filter(Problems.url == problem_url).first()
            return result
        except Exception as e:
            print("Ошибка получения данных из БД (get_problem_info):\n" + str(e))
            return {}