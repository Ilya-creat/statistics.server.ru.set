#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import configparser
import datetime
import os
import sqlite3
import threading
from ast import literal_eval

import requests
from flask import Flask, render_template, url_for, redirect, g, flash, request, make_response, \
    jsonify, abort, session
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import mistune
from werkzeug.security import generate_password_hash, check_password_hash

from BACKEND.models.dataBase import DATABASE
from BACKEND.models.forms import LoginForm, RegisterForm, ForgotForm, SendForm, EditProfile, ProblemsCreateForm, \
    ProblemSettingsTagForm, ProblemSettingsTagsForm, \
    ProblemSettingsResourcesForm, ProblemSettingsDataForm
from BACKEND.models.permissions_func import PermFunc
from BACKEND.models.user_login import UserLogin
from BACKEND.models.testing import Testing, ErrorTesting
from BACKEND.models.smtp import SMTP
from dotenv import load_dotenv, find_dotenv
import markdown
import markdown.extensions.fenced_code
from BACKEND.models.validate import check_image, check_user_status
from BACKEND.models.permissions import Permissions
import psutil
import platform
import BACKEND.models.config as cnfg

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
login_manager.login_view = 'main'
login_manager.login_message = "Авторизуйтесь для просмотра данной странички"
login_manager.login_message_category = "error"
url_locale = os.getcwd()  # "/var/www/statistics_judge/statistics_judge"  # "/var/www/statistics_judge/statistics_judge"
testing = Testing()
permissions = Permissions()
perm_func = PermFunc()


@login_manager.user_loader
def load_user(user_id):
    return UserLogin().fromDB(user_id, dbase)


dbase = DATABASE(app.config["DATABASE"])
task = None

paket = {
    "header": cnfg.header,
    "date_release": cnfg.date_release,
    "url": cnfg.url,
}


@app.route('/', methods=["POST", "GET"])
def main():
    if current_user.is_authenticated:
        user_permissions = permissions.get_permission(current_user.get_permissions())
        res_menu = perm_func.check_menu(user_permissions)
        menu = res_menu["default_menu"]
        admin_menu = res_menu["admin_menu"]
        nm = request.args.get("page")
        page = 1 if not nm else int(nm)
        posts = list(reversed(dbase.get_posts()))
        mx_page = 1 + (max(len(posts) - 5, 0)) // 6 + (1 if (max(len(posts) - 5, 0)) % 6 else 0)
        if page < 1:
            return redirect('/')
        elif page > mx_page:
            return redirect(f'/?page={mx_page}')
        for post in posts:
            post.times = datetime.datetime.strftime(post.times, "%d %B %Y %H:%M")
        if menu:
            return render_template('main.html',
                                   auth=True,
                                   header=paket["header"],
                                   date_release=paket["date_release"],
                                   url=paket["url"],
                                   menu=menu,
                                   admin_menu=admin_menu,
                                   user={
                                       "img-user": current_user.get_image(),
                                       "name": current_user.get_name(),
                                       "role": user_permissions["name-ru"],
                                       "profile_id": current_user.get_id(),
                                       "register": current_user.get_register(),
                                       "color": user_permissions["color"]
                                   },
                                   posts=posts,
                                   page=page,
                                   mx_page=mx_page
                                   )
        else:
            return redirect('/ban?account=YOU^_^')
    else:
        form_log = LoginForm()
        if form_log.validate_on_submit():
            user = dbase.get_user_by_email(form_log.indif.data)
            if user and check_password_hash(user.psw, form_log.psw.data):
                userlogin = UserLogin().create(user)
                rm = form_log.remember.data
                login_user(userlogin, remember=rm)
                flash('Авторизация прошла успешно!', category='success')
                return redirect(request.args.get('next') or '/')

            flash('Неверный Email/Логин или пароль!', category='error')

        return render_template('loginforms.html',
                               form_log=form_log,
                               header=paket["header"],
                               date_release=paket["date_release"],
                               url=paket["url"],
                               header_map={'Регистрация': '/register'})


@app.route('/register', methods=["POST", "GET"])
def register():
    form_reg = RegisterForm(dbase)
    print(form_reg.errors)
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
                           header=paket["header"],
                           date_release=paket["date_release"],
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
                                   header=paket["header"],
                                   date_release=paket["date_release"],
                                   header_map={'Обратно': '/'})
        return render_template('forgot.html',
                               forms=True,
                               token=token,
                               form_forgot=form_forgot,
                               header=paket["header"],
                               date_release=paket["date_release"],
                               header_map={'Обратно': '/'})
    elif not token:
        return render_template('forgot.html',
                               forms=False,
                               error="INVALID_TOKEN",
                               url=paket["url"],
                               header=paket["header"],
                               date_release=paket["date_release"],
                               header_map={'Обратно': '/'})
    else:
        return render_template('forgot.html',
                               forms=False,
                               error="TOKEN_IS_OUTDATED",
                               url=paket["url"],
                               header=paket["header"],
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
            if not smtp.send_email_for_password(paket["url"], token):
                flash('Произошла ошибка! Повторите операцию позже!',
                      category='error')
            else:
                flash('Письмо было отправлено!',
                      category='success')
                return redirect('/')
        return render_template('send.html',
                               forms=True,
                               form_send=send_form,
                               type_=type_,
                               url=paket["url"],
                               header=paket["header"],
                               date_release=paket["date_release"],
                               header_map={'Обратно': '/'})
    return render_template('send.html',
                           forms=False,
                           error="INVALID_TYPE",
                           url=paket["url"],
                           header=paket["header"],
                           date_release=paket["date_release"],
                           header_map={'Обратно': '/'})


@app.route('/profile/<int:user_id>')
@login_required
def profile(user_id):
    if user_id == current_user.get_id():
        profile_form = EditProfile()
        if current_user.get_status() in [1, 2]:
            return render_template('profile.html',
                                   header=HEADER,
                                   date_release=date_release,
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
                                   date_release=date_release,
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
                                   date_release=date_release,
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
                                   date_release=date_release,
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
                                   date_release=date_release,
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
                                   date_release=date_release,
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


@app.route('/post/<int:id_>', methods=["GET"])
@login_required
def posts_read(id_):
    user_permissions = permissions.get_permission(current_user.get_permissions())
    res_menu = perm_func.check_menu(user_permissions)
    menu = res_menu["default_menu"]
    admin_menu = res_menu["admin_menu"]
    if menu:
        note_md = dbase.get_post(id_)
        if note_md:
            import pymdownx.arithmatex as arithmatex
            md_template = markdown.markdown(
                note_md.content_ru, extensions=[
                    "fenced_code",
                    "tables",
                    "pymdownx.inlinehilite",
                    "pymdownx.superfences",
                    "toc",
                    "abbr",
                    "attr_list",
                    "def_list",
                    "footnotes",
                    "md_in_html",
                    "admonition",
                    "codehilite",
                    "legacy_attrs",
                    "legacy_em",
                    "meta",
                    "nl2br",
                    "sane_lists",
                    "wikilinks",
                    "mdx_emdash",
                    "bs4md",
                    "admonition",
                    "legacy_attrs",
                    "legacy_em",
                    "nl2br",
                    "sane_lists",
                    "smarty",
                    "meta"
                ],
                extension_configs={"pymdownx.inlinehilite": {
                    "custom_inline": [
                        {"name": "math", "class": "arithmatex",
                         "format": arithmatex.arithmatex_inline_format(which="generic")}
                    ]
                },
                    "pymdownx.superfences": {
                        "custom_fences": [
                            {"name": "math", "class": "arithmatex",
                             "format": arithmatex.arithmatex_fenced_format(which="generic")}
                        ]
                    }
                }
            )
            status_time = 1 if (datetime.datetime.strptime(str(note_md.times),
                                                           "%Y-%m-%d %H:%M:%S.%f") >= datetime.datetime.today() - datetime.timedelta(
                hours=24)) else 0
            note_md.times = datetime.datetime.strftime(note_md.times, "%d %B %Y %H:%M")
            return render_template('posts.html',
                                   auth=True,
                                   header=paket["header"],
                                   date_release=paket["date_release"],
                                   url=paket["url"],
                                   menu=menu,
                                   admin_menu=admin_menu,
                                   user={
                                       "img-user": current_user.get_image(),
                                       "name": current_user.get_name(),
                                       "role": user_permissions["name-ru"],
                                       "profile_id": current_user.get_id(),
                                       "register": current_user.get_register(),
                                       "color": user_permissions["color"]
                                   },
                                   note_md=md_template,
                                   note_name=note_md.name_ru,
                                   note_time=note_md.times,
                                   status_time=status_time
                                   )
        else:
            return redirect('/')
    else:
        return redirect('/ban?account=YOU^-^')


@app.route('/problems', methods=["POST", "GET"])
@app.route('/problems/edit')
@login_required
def problems():
    problems_create_form = ProblemsCreateForm()
    user_permissions = permissions.get_permission(current_user.get_permissions())
    res_menu = perm_func.check_menu(user_permissions)
    menu = res_menu["default_menu"]
    admin_menu = res_menu["admin_menu"]
    if menu:
        if problems_create_form.validate_on_submit():
            section_problem = problems_create_form.section.data
            if section_problem == '.sport-programming':
                type_problem = problems_create_form.sport_programming.data
            elif section_problem == '.artificial-intelligence':
                type_problem = problems_create_form.artificial_intelligence.data
            elif section_problem == '.machine-learn':
                type_problem = problems_create_form.machine_learn.data
            elif section_problem == '.test':
                type_problem = problems_create_form.test.data
            else:
                flash("Произошла ошибка!", "error")
                return redirect(url_for('problems'))
            if dbase.create_problem(section_problem, type_problem, current_user.get_id()):
                flash("Задача была успешно создана!", "success")
                return redirect(url_for('problems'))
            else:
                flash("Произошла ошибка!", "error")
                return redirect(url_for('problems'))
        users_problems = reversed(dbase.get_user_problems(current_user.get_id()))
        return render_template('problems.html',
                               auth=True,
                               header=paket["header"],
                               date_release=paket["date_release"],
                               url=paket["url"],
                               menu=menu,
                               admin_menu=admin_menu,
                               user={
                                   "img-user": current_user.get_image(),
                                   "name": current_user.get_name(),
                                   "role": user_permissions["name-ru"],
                                   "profile_id": current_user.get_id(),
                                   "register": current_user.get_register(),
                                   "color": user_permissions["color"]
                               },
                               problems_create_form=problems_create_form,
                               users_problems=users_problems
                               )
    else:
        return redirect('/ban?account=YOU^-^')


@app.route('/problems/edit/<string:problems>/')
@login_required
def edit_problems(problems):
    user_permissions = permissions.get_permission(current_user.get_permissions())
    res_menu = perm_func.check_menu(user_permissions)
    menu = res_menu["default_menu"]
    admin_menu = res_menu["admin_menu"]
    if menu:
        get_perm = perm_func.get_user_problem_permissions(dbase.get_user_problem_permissions(problems), problems,
                                                          current_user.get_id())
        perms_problems = perm_func.check_problem_permission(get_perm)
        problem_info = dbase.get_problem_info(problems)
        if not get_perm:
            return abort(404)
        if problem_info.section == ".sport-programming" and problem_info.type == ".standard":
            forms = {
                "settings-tech-tag": ProblemSettingsTagForm(),
                "settings-resources": ProblemSettingsResourcesForm(),
                "settings-data": ProblemSettingsDataForm(),
                "settings-testings": None,
                "settings-tags": ProblemSettingsTagsForm()
            }
            return render_template('problem.html',
                                   auth=True,
                                   header=paket["header"],
                                   date_release=paket["date_release"],
                                   url=paket["url"],
                                   menu=menu,
                                   admin_menu=admin_menu,
                                   user={
                                       "img-user": current_user.get_image(),
                                       "name": current_user.get_name(),
                                       "role": user_permissions["name-ru"],
                                       "profile_id": current_user.get_id(),
                                       "register": current_user.get_register(),
                                       "color": user_permissions["color"]
                                   },
                                   problem_url=problems,
                                   users_problem_perms=perms_problems,
                                   )
        return abort(404)
    else:
        return redirect('/ban?account=YOU^-^')


@app.route('/disable/reload/<string:page>', methods=["POST", "GET"])
@login_required
def disable_reload_page(page):
    user_permissions = permissions.get_permission(current_user.get_permissions())
    res_menu = perm_func.check_menu(user_permissions)
    menu = res_menu["default_menu"]
    if menu:
        problem_id = request.form["problem_id"]
        page_type = request.form["page_type"]
        get_perm = perm_func.get_user_problem_permissions(dbase.get_user_problem_permissions(problem_id), problem_id,
                                                          current_user.get_id())
        # perms_problems = perm_func.check_problem_permission(get_perm)
        if not get_perm:
            return abort(404)
        if page == 'problems':
            if page_type == "settings":
                problem_info = dbase.get_problem_info(problem_id)
                if problem_info.section == ".sport-programming" and problem_info.type == ".standard":
                    forms = {
                        "settings-tech-tag": ProblemSettingsTagForm(),
                        "settings-resources": ProblemSettingsResourcesForm(),
                        "settings-data": ProblemSettingsDataForm(),
                        "settings-testings": None,
                        "settings-tags": ProblemSettingsTagsForm()
                    }
                    return render_template("patterns/problem-settings.html",
                                           forms=forms,
                                           url=paket["url"]
                                           )
                return "1"
            return "1"
    return "._."


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из аккаунта', category='success')
    return redirect(url_for('main'))


@app.errorhandler(404)
def not_found(error):
    return render_template('errors/not_found.html')


@app.route('/ban', methods=["GET", "POST"])
@login_required
def ban():
    if len(permissions.get_permission(current_user.get_permissions())["permissions"]) == 0:
        return render_template("errors/ban.html")
    else:
        return redirect('/')


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
