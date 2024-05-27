from flask_wtf import FlaskForm, Form
from wtforms import StringField, SubmitField, BooleanField, PasswordField, FileField, SelectField, IntegerField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, NumberRange


class ProblemSettingsTagForm(Form):
    tag = StringField("Технический тег задачи",
                      validators=[DataRequired(),
                                  Length(min=1, max=20, message="Тег должен содержать "
                                                                "не менее 1 и не более "
                                                                "20 символов")],
                      )


class ProblemSettingsResourcesForm(Form):
    time_limit = IntegerField("Лимит времени",
                              validators=[DataRequired(),
                                          NumberRange(min=200, max=15000)
                                          ])
    memory_limit = IntegerField("Лимит памяти",
                                validators=[DataRequired(),
                                            NumberRange(min=4, max=2048)
                                            ])


class ProblemSettingsDataForm(Form):
    input_data = StringField("Ввод данных", validators=[DataRequired(),
                                                        Length(min=3, max=10, message="Название файла не корректно")]
                             )
    output_data = StringField("Вывод данных", validators=[DataRequired(),
                                                          Length(min=3, max=10, message="Название файла не корректно")]
                              )
    submit = SubmitField("Сохранить")


class ProblemSettingsTagsForm(Form):
    tags = StringField("Теги")
