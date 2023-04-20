import configparser
import datetime
import sqlite3


class SQL:
    def __init__(self, db):
        self.__db = db
        self.__cur = db.cursor()  # работа с БД
