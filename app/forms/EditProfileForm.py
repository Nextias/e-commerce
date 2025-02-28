import phonenumbers
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, ValidationError


class EditProfileForm(FlaskForm):
    first_name = StringField('Имя', validators=[DataRequired()])
    last_name = StringField('Фамилия', validators=[DataRequired()])
    phone_number = StringField('Номер телефона')
    about_me = StringField('Обо мне')
    address = StringField('Адрес')
    submit = SubmitField('Подтвердить')

    def validate_phone_number(form, field):
        if len(field.data) > 16:
            raise ValidationError('Неверный номер телефона.')
        try:
            input_number = phonenumbers.parse(field.data)
            if not (phonenumbers.is_valid_number(input_number)):
                raise ValidationError('Неверный номер телефона.')
        except ValidationError:
            input_number = phonenumbers.parse("+1"+field.data)
            if not (phonenumbers.is_valid_number(input_number)):
                raise ValidationError('Неверный номер телефона.')
