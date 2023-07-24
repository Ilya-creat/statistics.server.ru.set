import os
import sqlite3

from flask import make_response, jsonify
from flask_restful import Resource, reqparse
from werkzeug.security import generate_password_hash, check_password_hash

from API.sql import SQL
from BACKEND.models.dataBase import DATABASE
from BACKEND.models.config import VPS_PATH
parser_login = reqparse.RequestParser()
parser_login.add_argument('token', help='-', required=True)

data_client = reqparse.RequestParser()
data_client.add_argument('token', help='-', required=True)
db = None
if 'API' in os.path.abspath(os.curdir):
    db = sqlite3.Connection(f"{os.path.abspath(os.curdir)}/../dbase.db", check_same_thread=False)
elif os.path.abspath(os.curdir) != "/":
    db = sqlite3.Connection(f"{os.path.abspath(os.curdir)}/BACKEND/dbase.db", check_same_thread=False)
else:
    db = sqlite3.Connection(os.path.join(VPS_PATH, 'dbase.db'), check_same_thread=False)
db.row_factory = sqlite3.Row
global_sql = DATABASE(db)


class Info(Resource):
    def post(self):
        response = jsonify({
            'http_code': 200,
            'status': "ok",
            'info': 'statistics-judging-api'
        })
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response

    def get(self):
        response = jsonify({
            'http_code': 200,
            'status': "ok",
            'info': 'statistics-judging-api'
        })
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response
