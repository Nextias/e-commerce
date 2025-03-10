import re

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError


class EditProfileForm(FlaskForm):
    """Форма редактирования профиля."""
    first_name = StringField('Имя', validators=[DataRequired(),
                                                Length(max=30)])
    last_name = StringField('Фамилия', validators=[DataRequired(),
                                                   Length(max=30)])
    phone_number = StringField('Номер телефона', validators=[DataRequired(),
                                                             Length(max=20)])
    about_me = StringField('Обо мне', validators=[DataRequired(),
                                                  Length(max=140)])
    address = StringField('Адрес', validators=[DataRequired(),
                                               Length(max=60)])
    submit = SubmitField('Подтвердить')

    def validate_phone_number(form, field):
        """Валидация телефонного номера."""
        phone_pattern = re.compile(r'^\+?[0-9\s\-]{7,}$')

        if not phone_pattern.match(field.data):
            raise ValidationError('Неверный формат номера.')
