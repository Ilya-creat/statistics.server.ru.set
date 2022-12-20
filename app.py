#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import os
import asyncio
import collections
import concurrent.futures
import configparser
import os
import sqlite3
import threading
from ast import literal_eval

from flask import Flask, render_template, url_for, redirect, g, flash, request, make_response, \
    jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from Models.FDataBase import FDataBase
from Models.Forms import LoginForm, RegisterForm
from Models.TaskDataBase import TaskDataBase
from Models.UserLogin import UserLogin
from Models.testing import Testing, ErrorTesting
import time

SECRET_KEY = '5PAy8Kzr-cyMTeYAYPDL97ZUrBDpNcMhFQ2k_am_G0XHHcN9O7i0GTCKuz83k' \
             'DKFHKHENKCNOKFogofdgnoorro-6-03405tggtt#$jjdeksdk@#$$$$$'
app = Flask(__name__)
app.config.from_object(__name__)  # load configuration
app.config.update(dict(DATABASE=os.path.join(app.root_path, 'dbase.db')))  # переопределине пути к БД
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(app.root_path,
                           "static")  # Изначально пустой каталог, куда Flask соберёт всё при выполнении app.py
# collectstatic
STATICFILES_DIRS = [
    os.path.join(app.root_path, "static_dev"),
    # Каталог, куда нам нужно складывать статику проекта, не относящуюся к конкретному приложению
]
uploads_dir = os.path.join(app.instance_path, 'post_files')
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = "Авторизуйтесь для просмотра данной странички"
login_manager.login_message_category = "error"
url_locale = f"{os.getcwd()}" #"/var/www/www-root/data/www/server.statistics-online.ru"
testing = Testing()


@login_manager.user_loader
def load_user(user_id):
    return UserLogin().fromDB(user_id, dbase)


def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row  # преобразование в вид: словарей
    return conn


def conn_db_un_task():
    conn = sqlite3.connect(os.path.join(app.root_path, 'tasks.db'))
    conn.row_factory = sqlite3.Row  # преобразование в вид: словарей
    return conn


def create_db():
    """Вспомогательная функция создания таблиц БД"""
    db = connect_db()
    with app.open_resource('sq_db.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()


def get_db():
    """Соединение с БД, если оно еще не установлено"""
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db


def get_db_task():
    if not hasattr(g, 'link_db_task'):
        g.link_db_task = conn_db_un_task()
    return g.link_db_task


dbase = None
task = None


@app.before_request
def before_request():
    """Установление соединение с БД перед выполнения запроса"""
    global dbase, task
    db = get_db()
    dbase = FDataBase(db)
    ts = get_db_task()
    task = TaskDataBase(ts)


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'link_db_task'):
        g.link_db_task.close()


@app.route('/', methods=["POST", "GET"])
def login():
    if current_user.is_authenticated:
        return render_template('main.html',
                               header="Statistics.Server",
                               header_map={u'Создать задачу': u'/new_task', 'Создать контест': '/new_contest',
                                           'Модерация':
                                               '/verification', 'Задать вопрос': '/qt',
                                           f'Выйти (из {current_user.get_user()})':
                                               '/logout'},
                               my_task=task.my_task(current_user.get_id()),
                               news=dbase.get_news())
    form_log = LoginForm()
    if form_log.validate_on_submit():
        user = dbase.getUserByEmail(form_log.email.data)
        if user and check_password_hash(user['psw'], form_log.psw.data):
            userlogin = UserLogin().create(user)
            rm = form_log.remember.data
            login_user(userlogin, remember=rm)
            return redirect(request.args.get('next') or '/')

        flash('Неверный Email или пароль!', category='error')

    return render_template('loginforms.html',
                           form_log=form_log,
                           header="Statistics.Server",
                           header_map={'Регистрация': '/register'})


@app.route('/register', methods=["POST", "GET"])
def register():
    form_reg = RegisterForm()
    if form_reg.validate_on_submit():
        a = dbase.checkRegister('lk', 'email', form_reg.email.data)
        b = dbase.checkRegister('lk', 'user', form_reg.login.data)
        if not a:
            flash('Пользователь с таким EMAIL уже существует!', category='error')
            return redirect('/')
        elif not b:
            flash('Пользователь с таким Login уже существует!', category='error')
            return redirect('/')
        res = dbase.addUser(form_reg.login.data, form_reg.email.data, generate_password_hash(form_reg.psw1.data))
        if res:
            flash('Вы успешно зарегистрировались', category='success')
            return redirect('/')
    elif not form_reg.validate_on_submit():
        pass
    else:
        flash('Произошла ошибка при регистрации! Вернитесь в форму регистрации и проверте корректность данных!',
              category='error')
    return render_template('register.html',
                           form_reg=form_reg,
                           header="Statistics.Server",
                           header_map={'Обратно': '/'})


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из аккаунта', category='success')
    return redirect(url_for('login'))


@app.route('/post_news')
@login_required
def news():
    if current_user.get_status() == 'moder':
        return render_template('post.html',
                               header='Statistics.MyAdmin',
                               header_map={'Назад': '/'})
    else:
        return redirect('/')


@app.route('/add_post', methods=["POST", "GET"])
@login_required
def add_post():
    if current_user.is_authenticated:
        if current_user.get_status() == 'moder' and request.method == 'POST':
            ans = dbase.post_news(request.form['text'])
            if ans:
                flash('Оповещение сохранено!', 'success')
                return redirect('/')
            flash('Оповещение не сохранено!', 'error')
            return redirect('/')
        return redirect('/')
    else:
        return redirect('/')


@app.route('/api-v.1.0/<path:funct>', methods=['GET', 'POST'])
def apiReturn(funct):
    if funct == "get_task_all":
        arg = request.args.get('ids').split(',')
        json_ans = {}
        for i in arg:
            rearg = dbase.task_converter(i)
            config = configparser.ConfigParser()  # .ini файлы
            config.read(f'{url_locale}/instance/task/{rearg}/config.ini', encoding="utf-8")  # чтение
            contest_name = config['Config']['name']
            json_ans[i] = contest_name
        return make_response(jsonify(json_ans)), 200

    if funct == "get_task_name":
        config = configparser.ConfigParser()
        rearg = request.args.get('rearg')
        config.read(f'{url_locale}/instance/task/{rearg}/config.ini', encoding="utf-8")  # чтение
        return config['Config']['name'], 200

    if funct == "get_task":
        arg = request.args.get('id')
        rearg = dbase.task_converter(arg)
        config = configparser.ConfigParser()  # .ini файлы
        config.read(f'{url_locale}/instance/task/{rearg}/config.ini', encoding="utf-8")  # чтение
        contest_name = config['Config']['name']
        contest_time_limit = config['Config']['time_limit']
        contest_memory_limit = config['Config']['memory_limit']
        contest_input = config['Config']['input']
        contest_console = config['Config']['output']
        config.read(f'{url_locale}/instance/task/{rearg}/tests/tests.ini', encoding="utf-8")  # чтение
        ex = literal_eval(config['Examples']['ex'])
        with open(f'{url_locale}/instance/task/{rearg}/statments/legend.TEX', 'r', encoding="utf-8") as myfile:
            data = myfile.read()
        with open(f'{url_locale}/instance/task/{rearg}/statments/input.TEX', 'r', encoding="utf-8") as myfile:
            dt_input = myfile.read()
        with open(f'{url_locale}/instance/task/{rearg}/statments/output.TEX', 'r', encoding="utf-8") as myfile:
            dt_output = myfile.read()
        with open(f'{url_locale}/instance/task/{rearg}/statments/score.TEX', 'r', encoding="utf-8") as myfile:
            dt_score = myfile.read()
        with open(f'{url_locale}/instance/task/{rearg}/statments/notes.TEX', 'r', encoding="utf-8") as myfile:
            dt_notes = myfile.read()
        _dict_ = {}
        for i, j in ex.items():
            with open(f'{url_locale}/instance/task/{rearg}/tests/input/{i}.txt', 'r', encoding="utf-8") as myfile:
                exinp = myfile.read()
            with open(f'{url_locale}/instance/task/{rearg}/tests/output/{j}.txt', 'r', encoding="utf-8") as myfile:
                exout = myfile.read()
            for key in exinp:
                key.replace('\n', '<br>')
            for key in exout:
                key.replace('\n', '<br>')
            _dict_[exinp] = exout

        return make_response(jsonify(
            name=contest_name,
            time_limit=contest_time_limit,
            memory_limit=contest_memory_limit,
            c_input=contest_input,
            c_output=contest_console,
            task_text=data,
            task_input=dt_input,
            task_output=dt_output,
            score=dt_score,
            notes=dt_notes,
            examples=_dict_
        )), 200
    if funct == 'code':
        args_code = request.get_json()
        db = dbase.create(args_code['contest_id'], args_code['user_id'], args_code['_id'])
        compiler = testing.compiler(db)
        dbase.compile_lang(db, compiler[args_code["lang"]][3])
        new_file = open(f'{url_locale}/instance/post_files/{db}.{compiler[args_code["lang"]][1]}', 'w+', newline='',
                        encoding="utf-8")
        new_file.write(args_code['code'])
        new_file.close()
        rearg = dbase.task_converter(args_code['_id'])
        # _GLOBAL_DECISIONS_DEQUEUE_.append([args_code, db, rearg])
        try:
            threading.Thread(target=Testing().testing_module, args=(args_code, db, rearg)).start()
        except ErrorTesting:
            with sqlite3.connect("dbase.db") as con:
                cur = con.cursor()
                cur.execute(f"UPDATE code_task SET status = 'bruh' WHERE id = '{db}'")
                con.commit()
        return 'ok', 200
    if funct == 'testing_info':
        if request.args.get('my') == 'true':
            args = request.get_json()
            ans = dbase.get_testing_result(args['user_id'], args['tasks'], args['contest'])
            return make_response(jsonify(ans)), 200
        else:
            args = request.get_json()
            ans = dbase.get_testing_result_full(args['tasks'], args['contest'])
            return make_response(jsonify(ans)), 200
    return {}, 200


@app.route('/api-v.1.0', methods=['GET'])
def testing_source():
    return 'ok', 200


"""@app.route('/api-v.1.0/testing', methods=['GET', 'POST'])
def testing_proxy():
    files = request.files['file']
    files.save(os.path.join(uploads_dir, files.filename))
    p = subprocess.Popen(['python3', os.path.join(uploads_dir, files.filename)], shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    ans = p.communicate(input=b'1')[0]
    print(ans)
    return 'ok'"""

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
