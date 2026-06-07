from flask_wtf import FlaskForm
from wtforms import StringField, URLField, EmailField, SubmitField
from wtforms.validators import DataRequired, Email, Length, NumberRange, ValidationError, EqualTo
import string


class DemoForm(FlaskForm):
    def validator_url(self, field):
        url = field.data
        if "vk.com" in url or "ok.ru" in url:
            return
        raise ValidationError('URL должен содержать ссылки на ВК или ОК.')

    def validator_username(self, field):
        username = field.data
        if set(username) <= set(string.ascii_lowercase + string.digits + "_"):
            return
        raise ValidationError('Имя пользователя должно содержать только латинские буквы, цифры и подчеркивание.')

    username = StringField("Username", validators=[DataRequired(), validator_username])
    url = URLField("URL", validators=[DataRequired(), validator_url])
    email = EmailField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Submit")
