from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, FieldList, FormField, SubmitField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Optional, ValidationError  
from models import User
class LoginForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')

class RegistrationForm(FlaskForm):
    username = StringField('Юзернейм пользователя', validators=[DataRequired(), Length(min=4, max=30)])
    first_name = StringField('Имя пользователя')
    last_name = StringField('Фамилия пользователя')
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Подтвердите пароль', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Зарегистрироваться')
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Это имя пользователя уже занято')

class NewsForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired(), Length(min=6, max=200)])
    content = TextAreaField('Содержание', validators=[DataRequired(), Length(min=11, max=2048)])
    category = SelectField('Категория', coerce=int, validators=[DataRequired()])
    tags = StringField('Теги (через запятую)', description="Введите теги через запятую")
    is_private = BooleanField('Приватная новость ')#(видна только зарегестрированым пользователям)
    submit = SubmitField('Сохранить')

class CategoryForm(FlaskForm):
    name = StringField('Название категории', validators=[DataRequired(), Length(min=4, max=20)])
    submit = SubmitField('Сохранить')

class TagForm(FlaskForm):
    name = StringField('Название тега', validators=[DataRequired(), Length(min=2, max=20)])
    submit = SubmitField('Сохранить')
