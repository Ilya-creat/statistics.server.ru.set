#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import configparser
import datetime
import os
import sqlite3
import threading
from ast import literal_eval

from flask import Flask, render_template, url_for, redirect, g, flash, request, make_response, \
    jsonify, abort
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from BACKEND.models.dataBase import DATABASE
from BACKEND.models.forms import LoginForm, RegisterForm, ForgotForm, SendForm, EditProfile
from BACKEND.models.taskDataBase import TaskDataBase
from BACKEND.models.user_login import UserLogin
from BACKEND.models.testing import Testing, ErrorTesting
from BACKEND.models.smtp import SMTP
from dotenv import load_dotenv, find_dotenv

from BACKEND.models.validate import check_image, check_user_status
from BACKEND.models.permissions import Permissions
import psutil
import platform

load_dotenv('/var/www/statistics_judge/statistics_judge/.env')
# load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
app = Flask(__name__, subdomain_matching=True,
            static_folder='../WEB/static',
            template_folder='../WEB/templates')
app.config.from_object(__name__)  # load configuration
app.config.update(dict(DATABASE=os.path.join(app.root_path, 'dbase.db')))
app.config["SECRET_KEY"] = SECRET_KEY
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(app.root_path,
                           "../WEB/static")
STATICFILES_DIRS = [
    os.path.join(app.root_path, "static_dev"),
]
uploads_dir = os.path.join(app.instance_path, 'post_files')
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = "Авторизуйтесь для просмотра данной странички"
login_manager.login_message_category = "error"
url_locale = os.getcwd()  # "/var/www/statistics_judge/statistics_judge"  # "/var/www/statistics_judge/statistics_judge"
testing = Testing()
permissions = Permissions()

HEADER = "Statistics.Judging"
DATE_SNAP = "2023"
url = "http://127.0.0.1:5001"

menu = {
    "Главная": {
        "img-icon": "bx bx-grid-alt",
        "href": f"{url}/"
    }
}

default_menu = {
    "Главная": {
        "img-icon": "bx bx-grid-alt",
        "href": f"{url}/"
    },
    "Задачи": {
        "img-icon": "bx bx-folder",
        "href": f"{url}/problems"
    },
    "Контесты": {
        "img-icon": "bx bx-code-alt",
        "href": f"{url}/contests"
    },
    "Профиль": {
        "img-icon": "bx bx-user",
        "href": f"{url}/profile/1"
    },
    "Поддержка": {
        "img-icon": "bx bx-chat",
        "href": f"{url}/chats"
    },
}

moder_menu = {
    "Модерирование": {
        "img-icon": "bx bx-windows",
        "href": f"{url}/user_tasks"
    },
    "Система наказаний": {
        "img-icon": "bx bxs-meh-blank",
        "href": f"{url}/warns"
    }
}

admin_menu = {
    "Статус системы": {
        "img-icon": "bx bxs-server",
        "href": f"{url}/admins/status-system"
    },
    "Оповещения/Посты": {
        "img-icon": "bx bx-user",
        "href": f"{url}/admins/create-post"
    },
    "Модерирование": {
        "img-icon": "bx bx-windows",
        "href": f"{url}/user_tasks"
    },
    "Персонал": {
        "img-icon": "bx bxs-user-detail",
        "href": f"{url}/persons"
    },
    "Система наказаний": {
        "img-icon": "bx bxs-meh-blank",
        "href": f"{url}/warns"
    }
}


@login_manager.user_loader
def load_user(user_id):
    return UserLogin().fromDB(user_id, dbase)


dbase = DATABASE(app.config["DATABASE"])
task = None


@app.route('/', methods=["POST", "GET"])
def main():
    if current_user.is_authenticated:
        user_permissions = permissions.get_permission(current_user.get_permissions())
        if permissions.check_permission(user_permissions, 'sjudge.news.read', 'sjudge.admin.menu'):
            return render_template('main.html',
                                   header=HEADER,
                                   date_snap=DATE_SNAP,
                                   url=url,
                                   menu=default_menu,
                                   admin_menu=admin_menu,
                                   user={
                                       "img-user": current_user.get_image(),
                                       "name": current_user.get_name(),
                                       "role": user_permissions["name-ru"],
                                       "profile_id": current_user.get_id(),
                                       "register": current_user.get_register(),
                                       "color": user_permissions["color"]
                                   }
                                   )

        if permissions.check_permission(user_permissions, 'sjudge.news.read', 'sjudge.moder.menu'):
            return render_template('main.html',
                                   header=HEADER,
                                   date_snap=DATE_SNAP,
                                   url=url,
                                   menu=default_menu,
                                   admin_menu=moder_menu,
                                   user={
                                       "img-user": current_user.get_image(),
                                       "name": current_user.get_name(),
                                       "role": user_permissions["name-ru"],
                                       "profile_id": current_user.get_id(),
                                       "register": current_user.get_register(),
                                       "color": user_permissions["color"]
                                   }
                                   )
        if permissions.check_permission(user_permissions, 'sjudge.news.read', 'sjudge.author.menu'):
            return render_template('main.html',
                                   header=HEADER,
                                   date_snap=DATE_SNAP,
                                   url=url,
                                   menu=default_menu,
                                   admin_menu={},
                                   user={
                                       "img-user": current_user.get_image(),
                                       "name": current_user.get_name(),
                                       "role": user_permissions["name-ru"],
                                       "profile_id": current_user.get_id(),
                                       "register": current_user.get_register(),
                                       "color": user_permissions["color"]
                                   }
                                   )
        if permissions.check_permission(user_permissions, 'sjudge.news.read'):
            return render_template('main.html',
                                   header=HEADER,
                                   date_snap=DATE_SNAP,
                                   url=url,
                                   menu=menu,
                                   admin_menu={},
                                   user={
                                       "img-user": current_user.get_image(),
                                       "name": current_user.get_name(),
                                       "role": user_permissions["name-ru"],
                                       "profile_id": current_user.get_id(),
                                       "register": current_user.get_register(),
                                       "color": user_permissions["color"]
                                   }
                                   )
    else:
        form_log = LoginForm()
        if form_log.validate_on_submit():
            user = dbase.get_user_by_email(form_log.indif.data)
            if user and check_password_hash(user.psw, form_log.psw.data):
                userlogin = UserLogin().create(user)
                rm = form_log.remember.data
                login_user(userlogin, remember=rm)
                return redirect(request.args.get('next') or '/')
            user = dbase.get_user_by_login(form_log.indif.data)
            if user and check_password_hash(user.psw, form_log.psw.data):
                flash('Авторизация прошла успешно!', category='success')
                userlogin = UserLogin().create(user)
                rm = form_log.remember.data
                login_user(userlogin, remember=rm)
                return redirect(request.args.get('next') or '/')

            flash('Неверный Email/Логин или пароль!', category='error')

        return render_template('loginforms.html',
                               form_log=form_log,
                               url=url,
                               header=HEADER,
                               date_snap=DATE_SNAP,
                               header_map={'Регистрация': '/register'})


@app.route('/register', methods=["POST", "GET"])
def register():
    form_reg = RegisterForm(dbase)
    if form_reg.validate_on_submit():
        a = dbase.check_register_by_email(form_reg.email.data)
        b = dbase.check_register_by_login(form_reg.login.data)
        if not a:
            flash('Пользователь с таким EMAIL уже существует!', category='error')
            return redirect('/')
        elif not b:
            flash('Пользователь с таким логином уже существует!', category='error')
            return redirect('/')
        res = dbase.add_user(form_reg.login.data, form_reg.name.data, form_reg.email.data,
                             generate_password_hash(form_reg.psw1.data))
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
                           header=HEADER,
                           date_snap=DATE_SNAP,
                           header_map={'Обратно': '/'})


@app.route("/forgot", methods=["POST", "GET"])
def forgot():
    token = request.args.get('session_token')
    # print(dbase.check_session_token(token))
    if token and dbase.check_session_token(token):
        form_forgot = ForgotForm(dbase)
        if form_forgot.validate_on_submit():
            password = form_forgot.psw1.data
            result = dbase.overwrite_password(dbase.get_user_by_token_forgot(token), generate_password_hash(password))
            if result:
                dbase.close_session_token(token)
                flash("Пароль был успешно обновлен!", "success")
                return redirect('/')
            flash("Возникли проблемы... Восстанавливаем систему.", category="error")
            return render_template('forgot.html',
                                   forms=True,
                                   token=token,
                                   form_forgot=form_forgot,
                                   header=HEADER,
                                   date_snap=DATE_SNAP,
                                   header_map={'Обратно': '/'})
        return render_template('forgot.html',
                               forms=True,
                               token=token,
                               form_forgot=form_forgot,
                               header=HEADER,
                               date_snap=DATE_SNAP,
                               header_map={'Обратно': '/'})
    elif not token:
        return render_template('forgot.html',
                               forms=False,
                               error="INVALID_TOKEN",
                               url=url,
                               date_snap=DATE_SNAP,
                               header=HEADER,
                               header_map={'Обратно': '/'})
    else:
        return render_template('forgot.html',
                               forms=False,
                               error="TOKEN_IS_OUTDATED",
                               url=url,
                               header=HEADER,
                               header_map={'Обратно': '/'})


@app.route("/sending", methods=["POST", "GET"])
def refresh():
    type_ = request.args.get('type')
    if type_ == "forgot":
        send_form = SendForm(dbase)
        if send_form.validate_on_submit():
            smtp = SMTP(send_form.email.data)
            token = dbase.add_token_forgot(dbase.get_user_by_email(send_form.email.data).id)
            if not token:
                flash('Произошла ошибка! Повторите операцию позже!',
                      category='error')
            if not smtp.send_email_for_password(url, token):
                flash('Произошла ошибка! Повторите операцию позже!',
                      category='error')
            else:
                flash('Письмо было отправлено!',
                      category='success')
                return redirect('/')
        return render_template('send.html',
                               forms=True,
                               form_send=send_form,
                               url=url,
                               type_=type_,
                               date_snap=DATE_SNAP,
                               header=HEADER,
                               header_map={'Обратно': '/'})
    return render_template('send.html',
                           forms=False,
                           error="INVALID_TYPE",
                           url=url,
                           header=HEADER,
                           date_snap=DATE_SNAP,
                           header_map={'Обратно': '/'})


@app.route('/profile/<int:user_id>')
@login_required
def profile(user_id):
    if user_id == current_user.get_id():
        profile_form = EditProfile()
        if current_user.get_status() in [1, 2]:
            return render_template('profile.html',
                                   header=HEADER,
                                   date_snap=DATE_SNAP,
                                   url=url,
                                   menu=default_menu,
                                   admin_menu={},
                                   user={
                                       "img-user": current_user.get_image(),
                                       "name": current_user.get_name(),
                                       "role": dbase.get_status_info(current_user.get_status()),
                                       "role_id": current_user.get_status(),
                                       "profile_id": current_user.get_id(),
                                       "register": current_user.get_register(),
                                       "login": current_user.get_user(),
                                       "color": dbase.get_color(current_user.get_status())
                                   },
                                   profile_form=profile_form,
                                   user_id=True
                                   )
        if current_user.get_status() == 3:
            return render_template('profile.html',
                                   header=HEADER,
                                   date_snap=DATE_SNAP,
                                   url=url,
                                   menu=default_menu,
                                   admin_menu=moder_menu,
                                   user={
                                       "img-user": current_user.get_image(),
                                       "name": current_user.get_name(),
                                       "role": dbase.get_status_info(current_user.get_status()),
                                       "role_id": current_user.get_status(),
                                       "profile_id": current_user.get_id(),
                                       "register": current_user.get_register(),
                                       "login": current_user.get_user(),
                                       "color": dbase.get_color(current_user.get_status())
                                   },
                                   profile_form=profile_form,
                                   user_id=True
                                   )
        if current_user.get_status() in [4, 5, 6, 7]:
            return render_template('profile.html',
                                   header=HEADER,
                                   date_snap=DATE_SNAP,
                                   url=url,
                                   menu=default_menu,
                                   admin_menu=admin_menu,
                                   user={
                                       "img-user": current_user.get_image(),
                                       "name": current_user.get_name(),
                                       "role": dbase.get_status_info(current_user.get_status()),
                                       "role_id": current_user.get_status(),
                                       "profile_id": current_user.get_id(),
                                       "register": current_user.get_register(),
                                       "login": current_user.get_user(),
                                       "color": dbase.get_color(current_user.get_status())
                                   },
                                   profile_form=profile_form,
                                   user_id=True
                                   )
    else:
        if current_user.get_status() in [1, 2]:
            return render_template('profile.html',
                                   header=HEADER,
                                   date_snap=DATE_SNAP,
                                   url=url,
                                   menu=default_menu,
                                   admin_menu={},
                                   user={
                                       "img-user": current_user.get_image(),
                                       "name": current_user.get_name(),
                                       "role": dbase.get_status_info(current_user.get_status()),
                                       "role_id": current_user.get_status(),
                                       "profile_id": current_user.get_id(),
                                       "register": current_user.get_register(),
                                       "login": current_user.get_user(),
                                       "color": dbase.get_color(current_user.get_status())
                                   },
                                   error="NOT_PERMISSIONS",
                                   user_id=False
                                   )
        if current_user.get_status() == 3:
            return render_template('profile.html',
                                   header=HEADER,
                                   date_snap=DATE_SNAP,
                                   url=url,
                                   menu=default_menu,
                                   admin_menu=moder_menu,
                                   user={
                                       "img-user": current_user.get_image(),
                                       "name": current_user.get_name(),
                                       "role": dbase.get_status_info(current_user.get_status()),
                                       "role_id": current_user.get_status(),
                                       "profile_id": current_user.get_id(),
                                       "register": current_user.get_register(),
                                       "login": current_user.get_user(),
                                       "color": dbase.get_color(current_user.get_status())
                                   },
                                   error="NOT_PERMISSIONS",
                                   user_id=False
                                   )
        if current_user.get_status() in [4, 5, 6, 7]:
            return render_template('profile.html',
                                   header=HEADER,
                                   date_snap=DATE_SNAP,
                                   url=url,
                                   menu=default_menu,
                                   admin_menu=admin_menu,
                                   user={
                                       "img-user": current_user.get_image(),
                                       "name": current_user.get_name(),
                                       "role": dbase.get_status_info(current_user.get_status()),
                                       "role_id": current_user.get_status(),
                                       "profile_id": current_user.get_id(),
                                       "register": current_user.get_register(),
                                       "login": current_user.get_user(),
                                       "color": dbase.get_color(current_user.get_status())
                                   },
                                   error="NOT_PERMISSIONS",
                                   user_id=False
                                   )


@app.route('/profile/upload', methods=["POST", "GET"])
@login_required
def upload():
    if request.method == 'POST':
        if request.files['photo'] and check_image(request.files['photo'].filename):
            if dbase.upload_data(current_user.get_id(), request.form['name'], request.files['photo']):
                flash("Данные успешно обновлены!", "success")
            else:
                flash("Произошла ошибка...", "error")
        elif not request.files['photo'] and request.form['name']:
            if dbase.upload_data(current_user.get_id(), request.form['name']):
                flash("Данные успешно обновлены!", "success")
            else:
                flash("Произошла ошибка...", "error")
        else:
            flash("Операция отклонена", "info")
        return redirect(f'/profile/{current_user.get_id()}')
    else:
        return redirect(f'/profile/{current_user.get_id()}')






@app.route('/admins/create-post')
def create_post():
    if current_user.get_id() < 4:
        abort(404)
    return render_template('admins/post.html',
                           header=HEADER,
                           date_snap=DATE_SNAP,
                           url=url,
                           menu=default_menu,
                           admin_menu=admin_menu,
                           user={
                               "img-user": current_user.get_image(),
                               "name": current_user.get_name(),
                               "role": dbase.get_status_info(current_user.get_status()),
                               "role_id": current_user.get_status(),
                               "profile_id": current_user.get_id(),
                               "register": current_user.get_register(),
                               "color": dbase.get_color(current_user.get_status())
                           }
                           )


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из аккаунта', category='success')
    return redirect(url_for('main'))


@app.route('/api-v.1.0/<path:funct>', methods=['GET', 'POST'])
def apiReturn(funct):
    if funct == "get_task_all":
        arg = request.args.get('ids').split(',')
        json_ans = {}
        for i in arg:
            rearg = dbase.task_converter(i)
            config = configparser.ConfigParser()  # .ini файлы
            # print(url_locale)
            config.read(f'{url_locale}/BACKEND/instance/task/{rearg}/config.ini', encoding="utf-8")  # чтение
            # print(*config)
            contest_name = config['Config']['name']
            json_ans[i] = contest_name
        return make_response(jsonify(json_ans)), 200

    if funct == "get_task_name":
        config = configparser.ConfigParser()
        rearg = request.args.get('rearg')
        config.read(f'{url_locale}/BACKEND/instance/task/{rearg}/config.ini', encoding="utf-8")  # чтение
        return config['Config']['name'], 200

    if funct == "get_task":
        arg = request.args.get('id')
        rearg = dbase.task_converter(arg)
        config = configparser.ConfigParser()  # .ini файлы
        config.read(f'{url_locale}/BACKEND/instance/task/{rearg}/config.ini', encoding="utf-8")  # чтение
        contest_name = config['Config']['name']
        contest_time_limit = config['Config']['time_limit']
        contest_memory_limit = config['Config']['memory_limit']
        contest_input = config['Config']['input']
        contest_console = config['Config']['output']
        config.read(f'{url_locale}/BACKEND/instance/task/{rearg}/tests/tests.ini', encoding="utf-8")  # чтение
        ex = literal_eval(config['Examples']['ex'])
        with open(f'{url_locale}/BACKEND/instance/task/{rearg}/statments/legend.TEX', 'r', encoding="utf-8") as myfile:
            data = myfile.read()
        with open(f'{url_locale}/BACKEND/instance/task/{rearg}/statments/input.TEX', 'r', encoding="utf-8") as myfile:
            dt_input = myfile.read()
        with open(f'{url_locale}/BACKEND/instance/task/{rearg}/statments/output.TEX', 'r', encoding="utf-8") as myfile:
            dt_output = myfile.read()
        with open(f'{url_locale}/BACKEND/instance/task/{rearg}/statments/score.TEX', 'r', encoding="utf-8") as myfile:
            dt_score = myfile.read()
        with open(f'{url_locale}/BACKEND/instance/task/{rearg}/statments/notes.TEX', 'r', encoding="utf-8") as myfile:
            dt_notes = myfile.read()
        _dict_ = {}
        for i, j in ex.items():
            with open(f'{url_locale}/BACKEND/instance/task/{rearg}/tests/input/{i}.txt', 'r',
                      encoding="utf-8") as myfile:
                exinp = myfile.read()
            with open(f'{url_locale}/BACKEND/instance/task/{rearg}/tests/output/{j}.txt', 'r',
                      encoding="utf-8") as myfile:
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
        print(args_code)
        db = dbase.create(args_code['contest_id'], args_code['user_id'], args_code['_id'])
        compiler = testing.compiler(db)
        dbase.compile_lang(db, compiler[args_code["lang"]][3])
        new_file = open(f'{url_locale}/BACKEND/instance/post_files/{db}.{compiler[args_code["lang"]][1]}', 'w+',
                        newline='',
                        encoding="utf-8")
        new_file.write(args_code['code'])
        new_file.close()
        rearg = dbase.task_converter(args_code['_id'])
        # _GLOBAL_DECISIONS_DEQUEUE_.append([args_code, db, rearg])
        try:
            threading.Thread(target=Testing().testing_module, args=(args_code, db, rearg, url_locale)).start()
        except ErrorTesting:
            with sqlite3.connect("dbase.db") as con:
                cur = con.cursor()
                cur.execute(f"UPDATE code_task SET status = 'bruh' WHERE id = '{db}'")
                con.commit()
        return 'ok', 200
    if funct == 'testing_info':
        if request.args.get('my') == 'true':
            args = request.get_json()
            ans = dbase.get_testing_result(args['user_id'], args['tasks'], args['contest'], url_locale)
            return make_response(jsonify(ans)), 200
        else:
            args = request.get_json()
            ans = dbase.get_testing_result_full(args['tasks'], args['contest'], url_locale)
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


@app.errorhandler(404)
def not_found(error):
    return render_template('errors/not_found.html')


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
