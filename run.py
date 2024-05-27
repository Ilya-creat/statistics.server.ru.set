import datetime

from werkzeug.serving import run_simple

from BACKEND.config_app import app
import psutil

application = app

if __name__ == '__main__':
    run_simple('0.0.0.0', 5001, application, use_reloader=True, use_debugger=True, use_evalex=True,
               threaded=True)
