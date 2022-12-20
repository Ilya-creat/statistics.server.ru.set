import configparser
import datetime
import sqlite3

import requests


class FDataBase:
    def __init__(self, db):
        self.__db = db
        self.__cur = db.cursor()  # работа с БДc

    def checkRegister(self, base, name, forms):
        try:
            self.__cur.execute(f"SELECT COUNT() as `count` FROM {base} WHERE {name} LIKE '{forms}'")
            if self.__cur.fetchone()['count'] > 0:
                print(f'Пользователь с таким {forms} уже существует. . .')
                return False
            else:
                return True
        except sqlite3.Error as e:
            print("Ошибка получения запроса в БД:\n" + str(e))
            return False

    def addUser(self, login, email, hpsw):
        try:
            self.__cur.execute(f"SELECT COUNT() as `count` FROM lk WHERE email LIKE '{email}'")
            if self.__cur.fetchone()['count'] > 0:
                print('Пользователь с таким email уже существует. . .')
                return False

            tm = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=3)))
            self.__cur.execute("INSERT INTO lk VALUES(NULL, ?, ?, ?, ?, ?, NULL)",
                               (login, email, hpsw, tm.strftime("%Y-%m-%d %H.%M.%S"), hpsw))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка добавления пользователя в БД:\n" + str(e))
            return False
        return True

    def getUserByEmail(self, email):
        try:
            self.__cur.execute(f"SELECT * FROM lk WHERE email = '{email}' LIMIT 1")
            res = self.__cur.fetchone()
            if not res:
                print("Пользователь не найден")
                return False

            return res
        except sqlite3.Error as e:
            print("Ошибка получения данных из БД:\n" + str(e))
        return False

    def getUser(self, user_id):
        try:
            self.__cur.execute(f"SELECT * FROM lk WHERE id = '{user_id}' LIMIT 1")
            res = self.__cur.fetchone()
            if not res:
                print("Пользователь не найден")
                return False
            return res
        except sqlite3.Error as e:
            print("Ошибка получения данных из БД:\n" + str(e))
        return False

    def get_news(self):
        try:
            self.__cur.execute(f"SELECT * FROM news")
            text = self.__cur.fetchall()
            _dict_ = dict()
            for i in text:
                _dict_[i[0]] = i[1]
            return _dict_
        except sqlite3.Error as e:
            print("Ошибка получения данных из БД:\n" + str(e))
        return {}

    def post_news(self, text):
        try:
            self.__cur.execute(f"INSERT INTO news VALUES(?, ?)",
                               (datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=3))).strftime('%d-%m'
                                                                                                               '-%Y '
                                                                                                               '%H:%M'),
                                text)
                               )
            self.__db.commit()
            return True
        except sqlite3.Error as e:
            print("Ошибка сохранения данных из БД:\n" + str(e))
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