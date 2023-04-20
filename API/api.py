import os
import sqlite3
from datetime import timedelta

from flask import Flask, jsonify
from flask_restful import Api
from flask_jwt_extended import JWTManager
import API.resources
from flask_cors import CORS, cross_origin

application = Flask(__name__)
api = Api(application)
cors = CORS(application)
application.config['CORS_HEADERS'] = 'Content-Type'
application.config['JWT_SECRET_KEY'] = 'A3ACA9958A67A695BADF2F5A2BD5C'
jwt = JWTManager(application)
application.config['JWT_BLACKLIST_ENABLED'] = True
application.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']
application.permanent_session_lifetime = timedelta(days=365)

# API 1.0
api.add_resource(API.resources.Info, '/v1.0/')


@jwt.token_in_blocklist_loader
def check_if_token_in_blacklist(self, decrypted_token):
    return API.resources.global_sql.check_if_token_in_blacklist(decrypted_token['jti'])


if __name__ == '__main__':
    application.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
