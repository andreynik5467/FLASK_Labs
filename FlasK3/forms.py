import string
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError, EqualTo
from utils import load_json, save_json
from werkzeug.security import generate_password_hash, check_password_hash

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class RegistrationForm(FlaskForm):

    def validate_password(self, field):
        password = field.data
        if len(password) < 8:
            raise ValidationError("Пароль должен быть длиной не менее 8 символов.")
        if not len(set(string.digits) & set(password)):
            raise ValidationError("Пароль должен содержать цифры.")
        if not len(set(string.ascii_lowercase) & set(password)):
            raise ValidationError("Пароль должен содержать маленькие латинские буквы.")
        if not len(set(string.ascii_uppercase) & set(password)):
            raise ValidationError("Пароль должен содержать большие латинские буквы.")
        if not len(set(string.punctuation) & set(password)):
            raise ValidationError("Пароль должен содержать символы.")

    def validate_username(self, field):
        username = field.data
        user_dct = load_json("data", "user.json")
        if username in user_dct:
            raise ValidationError("Такой пользоваетель уже зарегистрирован.")
        if username in ["admin", "root", "superuser", "director", "chief", "boss"]:
            raise ValidationError("Такое имя пользоваетеля запрещено.")
        if not (set(username) <= set(string.ascii_lowercase + string.digits + "_")):
            raise ValidationError("Имя пользователя должно содержать латинские буквы, цифры и подчеркивание.")

    username = StringField("Имя пользователя",
        validators=[
            DataRequired(),
            Length(min=4, max=25, message="Имя пользователя должно быть длиной от 4 до 25 символов."),
            validate_username
            ])
    password = PasswordField("Пароль",
        validators=[
            DataRequired(),
            validate_password
            ])
    confirm = PasswordField("Повтор пароля",
        validators=[
            DataRequired(),
            EqualTo("password", message="Пароли должны совпадать.")
            ])
    submit = SubmitField("Регистрация")
