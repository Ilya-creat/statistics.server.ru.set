import datetime
import sqlite3
from ast import literal_eval


class TaskDataBase:
    def __init__(self, db):
        self.__db = db
        self.__cur = db.cursor()  # работа с БД

    def my_task(self, user):
        try:
            self.__cur.execute(f"SELECT id, name, author FROM task")
            task = self.__cur.fetchall()
            _dict_ = {}
            for elem in task:
                if int(user) in literal_eval(elem[2]):
                    _dict_[elem[0]] = elem[1]
            return _dict_
        except sqlite3.Error as e:
            print("Ошибка получения запроса в БД:\n" + str(e))
            return None
