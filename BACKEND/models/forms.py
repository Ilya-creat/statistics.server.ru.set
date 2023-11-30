from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, PasswordField, FileField, SelectField, IntegerField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, NumberRange

from BACKEND.models.validate import validate_login, validate_login_check, validate_email_check, validate_psw


class LoginForm(FlaskForm):
    indif = StringField("Email/Логин", validators=[DataRequired()], render_kw={"placeholder": "Email"})
    psw = PasswordField("Пароль", validators=[DataRequired(), Length(min=5, max=100, message="Пароль должен содержать "
                                                                                             "не менее 5 и не более "
                                                                                             "100 символов")],
                        render_kw={"placeholder": "Пароль"})
    remember = BooleanField("Запомнить меня", default=False)
    submit = SubmitField("Войти")


class RegisterForm(FlaskForm):
    login = StringField("Логин", validators=[DataRequired(), Length(min=5, max=15, message="Логин должен содержать "
                                                                                           "не менее 5 и не более "
                                                                                           "15 символов")],
                        render_kw={"placeholder": "Логин"}, id="LOGIN")
    email = StringField("Email", validators=[Email("Некорректный Email")], render_kw={"placeholder": "Email"},
                        id="EMAIL")
    name = StringField("Фамилия и имя",
                       validators=[DataRequired(),
                                   Length(min=3, max=20, message="Логин должен содержать "
                                                                 "не менее 3 и не более "
                                                                 "20 символов")],
                       render_kw={"placeholder": "Инициалы (Фамилия Имя)"}, id="NAMING"
                       )
    psw1 = PasswordField("Пароль", validators=[DataRequired(), Length(min=5, max=100, message="Пароль должен содержать "
                                                                                              "не менее 5 и не более "
                                                                                              "100 символов")],
                         render_kw={"placeholder": "Пароль"}, id="PSW1")
    psw2 = PasswordField("Повтор пароля",
                         validators=[DataRequired(),
                                     EqualTo('psw1', message="Пароли не совпадают")],
                         render_kw={"placeholder": "Повтор пароля"}, id="PSW2")
    submit = SubmitField("Регистрация")

    def __init__(self, db):
        super().__init__()
        self.db = db

    def validate_login(self, field):
        if not validate_login(field.data):
            raise ValidationError("Логин должен содеражать минимум 1 заглавный и прописной ENG символ.")
        if not validate_login_check(self.db, field.data):
            raise ValidationError("Аккаунт с таким логином уже существует!")

    def validate_password(self, field):
        if not validate_psw(field.data):
            raise ValidationError("Пароль должен содеражать минимум 1 заглавный и прописной ENG символ, а также цифру.")

    def validate_email(self, field):
        if not validate_email_check(self.db, field.data):
            raise ValidationError("Аккаунт с таким email уже существует!")


class ForgotForm(FlaskForm):
    psw1 = PasswordField("Новый пароль",
                         validators=[DataRequired(), Length(min=5, max=100, message="Пароль должен содержать "
                                                                                    "не менее 5 и не более "
                                                                                    "100 символов")],
                         render_kw={"placeholder": "Новый пароль"}, id="PSW1")
    psw2 = PasswordField("Обмновите пароль",
                         validators=[DataRequired(),
                                     EqualTo('psw1', message="Пароли не совпадают")],
                         render_kw={"placeholder": "Повтор пароля"}, id="PSW2")
    submit = SubmitField("Изменить пароль")

    def __init__(self, db):
        super().__init__()
        self.db = db

    def validate_psw1(self, field):
        if not validate_psw(field.data):
            raise ValidationError("Пароль должен содеражать минимум 1 заглавный и прописной ENG символ, а также цифру.")


class SendForm(FlaskForm):
    email = StringField("Email", validators=[Email("Некорректный Email")], render_kw={"placeholder": "Email"})
    submit = SubmitField("Отправить")

    def __init__(self, db):
        super().__init__()
        self.db = db

    def validate_email(self, field):
        if not self.db.get_user_by_email(field.data):
            raise ValidationError("Пользователь не найден.")


def FileSizeLimit(max_size_in_mb):
    max_bytes = max_size_in_mb * 1024 * 1024

    def file_length_check(form, field):
        if len(field.data.read()) > max_bytes:
            raise ValidationError(
                f'File size is too large. Max allowed: {max_size_in_mb} MB')
        field.data.seek(0)

    return file_length_check


class EditProfile(FlaskForm):
    photo = FileField('Обновить аватар', validators=[FileSizeLimit(max_size_in_mb=2)], id="files")
    name = StringField("Обновить инициалы",
                       validators=[
                           Length(min=3, max=20, message="Логин должен содержать "
                                                         "не менее 3 и не более "
                                                         "20 символов")],
                       render_kw={"placeholder": "Обновить инициалы (Фамилия Имя)"}, id="naming")
    submit = SubmitField("Изменить данные")


class ProblemsCreateForm(FlaskForm):
    section = SelectField(f'Выберете раздел:', choices=[
        (".sport-programming", "Спортивное программирование"),
        (".artificial-intelligence", "Исскуственный интеллект"),
        (".machine-learn", "Машинное обучение"),
        (".test", "Тест")
    ], validators=[DataRequired()])

    sport_programming = SelectField(f'Выберете тип', choices=[
        (".standard", "Стандартная"),
        (".interactive", "Интерактивная"),
        (".twice-run", "Двойной запуск"),
        (".open-tests", "Открытые тесты")
    ], default=1)

    artificial_intelligence = SelectField(f'Выберете тип', choices=[
        (".standard", "Стандартная"),
    ], default=1)

    machine_learn = SelectField(f'Выберете тип', choices=[
        (".standard", "Стандартная"),
    ], default=1)

    test = SelectField(f'Выберете тип', choices=[
        (".standard", "Текстовая"),
    ], default=1)

    submit = SubmitField("Создать задачу")


class ProblemSettingsTagForm(FlaskForm):
    tag = StringField("Технический тег задачи",
                      validators=[
                          Length(min=1, max=20, message="Тег должен содержать "
                                                        "не менее 1 и не более "
                                                        "20 символов")],
                      )
    submit = SubmitField("Сохранить")


class ProblemSettingsResourcesForm(FlaskForm):
    time_limit = IntegerField("Лимит времени",
                              validators=[
                                  NumberRange(min=200, max=15000)
                              ])
    memory_limit = IntegerField("Лимит памяти",
                                validators=[
                                    NumberRange(min=4, max=2048)
                                ])
    submit = SubmitField("Сохранить")


class ProblemSettingsDataForm(FlaskForm):
    input_data = StringField("Ввод данных")
    output_data = StringField("Вывод данных")
    submit = SubmitField("Сохранить")


class ProblemSettingsTagsForm(FlaskForm):
    tags = StringField("Теги")
