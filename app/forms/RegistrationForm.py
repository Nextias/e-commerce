import re

import sqlalchemy as sa
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import (DataRequired, Email, EqualTo, ValidationError,
                                Length)
from app import db
from app.models import User  # type: ignore[name-defined]


class RegistrationForm(FlaskForm):
    """Форма регистрации."""
    username = StringField('Имя пользователя', validators=[DataRequired(),
                                                           Length(max=64)])
    email = StringField('Адрес электронной почты',
                        validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password2 = PasswordField(
        'Повторить пароль', validators=[DataRequired(),
                                        EqualTo('password')])
    submit = SubmitField('Зарегистрироваться')

    def validate_username(self, username):
        user = db.session.scalar(
            sa.select(User).where(User.username == username.data))
        if user is not None:
            raise ValidationError('Используйте другое имя пользователя.')

    def validate_email(self, email):
        user = db.session.scalar(
            sa.select(User).where(User.email == email.data))
        if user is not None:
            raise ValidationError('Данный почтовый адрес уже занят.')

    def validate_password(self, password):
        if len(password.data) < 10:
            raise ValidationError(
                'Длина пароля должна быть не менее 10'
                ' символов, включая буквы в обоих регистрах и цифры.')
        elif not re.search(r"[A-Z]", password.data):
            raise ValidationError('Пароль должен содержать символы в'
                                  ' верхнем регистре.')
        if not re.search(r"[a-z]", password.data):
            raise ValidationError('Пароль должен содержать символы в'
                                  ' нижнем регистре.')
        if not re.search(r"[0-9]", password.data):
            raise ValidationError('Пароль должен содержать цифры.')
