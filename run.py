from werkzeug.serving import run_simple
from BACKEND.config_app import app

application = app

if __name__ == '__main__':
    run_simple('127.0.0.1', 5000, application, use_reloader=True, use_debugger=True, use_evalex=True,
               threaded=True)
