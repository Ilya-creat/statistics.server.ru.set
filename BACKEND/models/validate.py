import secrets
import flask
from flask import abort


def upper_char(text):
    for i in text:
        if i.isupper():
            return True
    return False


def lower_char(text):
    for i in text:
        if i.islower() and ord(i):
            return True
    return False


def digit_char(text):
    for i in text:
        if i.isdigit():
            return True
    return False


def eng_char(text):
    for i in text:
        # print(ord(i), i.isalpha())
        if ord(i) > 400 and i.isalpha():
            return False
    return True


def validate_login(login):
    return lower_char(login) and upper_char(login) and eng_char(login)


def validate_psw(psw):
    # print(psw, eng_char(psw))
    return lower_char(psw) and upper_char(psw) and digit_char(psw) and eng_char(psw)


def validate_login_check(db, login):
    return db.check_register_by_login(login)


def validate_email_check(db, email):
    return db.check_register_by_email(email)


def generation_token():
    return secrets.token_urlsafe()


def check_image(m):
    return m.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))


def check_user_status(current_user):
    if current_user.get_status() < 4:
        abort(404)
