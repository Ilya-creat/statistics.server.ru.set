from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, PasswordField
from wtforms.validators import DataRequired, Email, Length, EqualTo


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[Email("Некорректный Email")], render_kw={"placeholder": "Email"})
    psw = PasswordField("Пароль", validators=[DataRequired(), Length(min=5, max=100, message="Пароль должен содержать "
                                                                                             "не менее 5 и не более "
                                                                                             "100 символов")],
                        render_kw={"placeholder": "Пароль"})
    remember = BooleanField("Запомнить меня", default=False)
    submit = SubmitField("Войти")


class RegisterForm(FlaskForm):
    login = StringField("Login", validators=[DataRequired(), Length(min=5, max=100, message="Логин должен содержать "
                                                                                            "не менее 5 и не более "
                                                                                            "100 символов")],
                        render_kw={"placeholder": "Логин"})
    email = StringField("Email", validators=[Email("Некорректный Email")], render_kw={"placeholder": "Email"})
    psw1 = PasswordField("Пароль", validators=[DataRequired(), Length(min=5, max=100, message="Пароль должен содержать "
                                                                                              "не менее 5 и не более "
                                                                                              "100 символов")],
                         render_kw={"placeholder": "Пароль"})
    psw2 = PasswordField("Повтор пароля",
                         validators=[DataRequired(),
                                     EqualTo('psw1', message="Пароли не совпадают")],
                         render_kw={"placeholder": "Повтор пароля"})
    submit = SubmitField("Регистрация")
